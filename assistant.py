import asyncio
import json
import os
import re
import sys
from typing import Any, Optional, Tuple
import openai
from openai import AsyncOpenAI

import pprint

from functions.calculo_lambrin_ext import calculate_cost_lambrin_exterior
from functions.calculo_lambrin_interior import calculate_cost_lambrin_interior
from functions.calculo_muro_durock import calculate_cost_muro_durock
from functions.calculo_plafon import calcular_costo_plafon_reticular
from functions.calculo_plafon_corrido import calculate_plafon_corrido
from functions.muro_interior import calcular_costo_muro_interior

from thread_types import UserThreads, SenderThread
from twilio_utils import send_responses_with_twilio

IS_REPLIT = 'REPLIT_USER' in os.environ

if IS_REPLIT:
    from replit import db
else:
    db = {}

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')


#gpt-4o-mini

# Replace with your actual OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]
client = AsyncOpenAI()
bclient = client.beta


def get_assistant_id_from_sender():
    return "asst_7dELb6O4IjQClbiiQA2EIzME"

def handle_requires_action(tool_call):
    logger.info(f"Handling requires action")
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print(f"Tool call: {name} with arguments: {arguments}")
    result = {}
    if name == "calcular_costo_muro_interior":
        result = calcular_costo_muro_interior(arguments["ancho"],
                                              arguments["largo"],
                                              arguments["caras"])

    elif name == "calcular_costo_muro_durock":
        result = calculate_cost_muro_durock(arguments["ancho"],
                                            arguments["largo"],
                                            arguments["caras"])

    elif name == "calcular_costo_plafon_reticular":
        result = calcular_costo_plafon_reticular(arguments["largo"],
                                                 arguments["ancho"],
                                                 arguments["tipo_plafon"])

    elif name == "calcular_costo_plafon_corrido":
        result = calculate_plafon_corrido(arguments["largo"], arguments["ancho"])

    elif name == "calcular_costo_lambrin_interior":
        result = calculate_cost_lambrin_interior(arguments["area"])

    elif name == "calcular_costo_lambrin_exterior":
        result = calculate_cost_lambrin_exterior(arguments["area"])

    print(f"Tool calculation result: {result}")
    return result

async def run_thread(thread: SenderThread,
                     sender: str,
                     profile_name: str) -> tuple[Any, bool]:
    """Process the thread run based on its status."""
    max_retries = 3
    retry_delay = 2  # seconds
    run_timeout = 20  # seconds
    sent_thinking_message = False

    print(f"Running thread with profile name: {profile_name}")
    for attempt in range(max_retries):
        try:
            # Create run
            run = await client.beta.threads.runs.create(
                thread_id=thread.thread_id,
                assistant_id=thread.assistant,
                # Forcing file search all the time
                #tool_choice={"type": "file_search"}
                additional_instructions=(
                  f"Menciona el nombre del usuario que es {profile_name} "
                  f"al inicio de la conversación y al finalizar la respuesta. "
                  f"Si el nombre esta vacio, no lo menciones."
                )
            )

            logger.info(f"Run created with ID: {run.id}")
            logger.info(f"Available tools: {run.tools}")  # Log available tools

            async def check_run_status():
                nonlocal run, sent_thinking_message
                while True:
                    if run.status in ["queued", "in_progress"]:
                        logger.info(f"Run status queued or in progress: {run.status}")
                        run = await client.beta.threads.runs.retrieve(
                            thread_id=thread.thread_id,
                            run_id=run.id,
                        )
                        await asyncio.sleep(1)  # Add a small delay to prevent tight looping
                    elif run.status == "requires_action":
                        logger.info(f"Run status requires_action: {run.status}")
                        required_action = run.required_action
                        logger.info(f"Required action: {required_action}")
                        tool_calls = required_action.submit_tool_outputs.tool_calls
                        logger.info(f"Tool calls: {tool_calls}")

                        tool_outputs = []
                        for tool_call in tool_calls:
                            logger.info(f"Tool call: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
                            result = handle_requires_action(tool_call)
                            logger.info(f"Tool result: {result}")

                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(result),
                            })

                        run = await client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs,
                        )

                    else:
                        return run

            try:
                run = await asyncio.wait_for(check_run_status(), timeout=run_timeout)
                return run, sent_thinking_message
            except asyncio.TimeoutError:
                logger.warning(f"Run timed out after {run_timeout} seconds. Cancelling...")
                await client.beta.threads.runs.cancel(thread_id=thread.thread_id, run_id=run.id)
                raise

        except Exception as e:
            if "A run is already active" in str(e) and attempt < max_retries - 1:
                logger.warning(f"A run is already active. Sending thinking message and retrying in {retry_delay} seconds...")
                if not sent_thinking_message:
                    await send_responses_with_twilio(to=sender, body="I'm thinking about your question. I'll have an answer for you in a few seconds.")
                    sent_thinking_message = True
                await asyncio.sleep(retry_delay)
            else:
                raise

    raise Exception("Failed to create or complete the run after multiple attempts.")


async def submit_message_to_thread(thread: SenderThread,
                             user_message: str):
    try:
        await bclient.threads.messages.create(thread_id=thread.thread_id,
                                        role="user",
                                        content=user_message)

        # Add the message to the thread's messages list
        thread.add_message(role="user", content=user_message)

    except openai.BadRequestError as e:
        raise Exception("Failed to submit message to OpenAI.") from e

    except Exception as e:
        raise Exception("An unexpected error occurred while submitting the message.") from e


async def get_or_create_thread_in_openai(user_threads: UserThreads) -> SenderThread:
    """Check if any thread for the user exists in OpenAI; if not, create a new one."""
    for thread in user_threads.threads:
        try:
            # Attempt to retrieve the thread from OpenAI
            existing_thread = await bclient.threads.retrieve(thread_id=thread.thread_id)
            # If the thread exists, return it
            if existing_thread:
                print(f"Found existing thread: {thread.thread_id} in OpenAI. Will use it.")
                return thread  # Return the existing thread from local storage
        except openai.NotFoundError:
            # If the thread does not exist, continue checking the next thread
            print(f"Thread with ID {thread.thread_id} does not exist in OpenAI.")

    # If no existing thread is found, create a new one
    new_thread = await bclient.threads.create()
    summary = summarize_previous_threads(user_threads)

    new_thread_obj = SenderThread(new_thread.id,
                                  "asst_7dELb6O4IjQClbiiQA2EIzME",
                                  summary)

    user_threads.add_thread(new_thread_obj)

    print(f"will create new: {user_threads.find_thread(new_thread.id)}")
    # Summarize previous thread information if needed
    # Add the new thread to the user's threads with its summary
    return new_thread_obj



def summarize_previous_threads(user_threads: UserThreads) -> str:
    """Summarize information from previous threads."""
    # Implement your summarization logic here
    summaries = [thread.summary for thread in user_threads.threads if thread.summary]
    return " ".join(summaries)


def get_user_threads(sender_phone_number: str) -> UserThreads:
    if sender_phone_number not in db:
        logger.info(f"Creating new UserThreads object for {sender_phone_number}")
        user_threads = UserThreads(sender_phone_number)
    else:
        logger.info(f"Retrieving UserThreads for {sender_phone_number}")
        user_threads_dict = json.loads(db[sender_phone_number])
        user_threads = UserThreads.from_dict(user_threads_dict)
    return user_threads


def save_user_threads(sender_phone_number: str, user_threads: UserThreads):
    logger.info(f"Saving UserThreads for {sender_phone_number}")
    db[sender_phone_number] = json.dumps(user_threads.to_dict())


def extract_last_message_content(response):
  last_message = response.data[0]
  last_message_content = last_message.content[0].text.value
  return last_message_content


def print_sync_cursor_page(sync_cursor_page):
    """Prints the SyncCursorPage[Message] object in a readable format."""
    print(f"Object Type: {sync_cursor_page.object}")
    print(f"Has More: {sync_cursor_page.has_more}")
    print(f"First ID: {sync_cursor_page.first_id}")
    print(f"Last ID: {sync_cursor_page.last_id}")
    print("Messages:")

    for message in sync_cursor_page.data:
        print(f"  Message ID: {message.id}")
        print(f"  Assistant ID: {message.assistant_id}")
        print(f"  Role: {message.role}")
        print(f"  Created At: {message.created_at}")
        print(f"  Content:")
        for content_block in message.content:
            print(f"    - Type: {content_block.type}")
            print(f"      Text: {content_block.text.value}")
        print(f"  Thread ID: {message.thread_id}")
        print(f"  Run ID: {message.run_id}")
        print(f"  Status: {message.status}")
        print(f"  Completed At: {message.completed_at}")
        print(f"  Attachments: {message.attachments}")
        print("")


def display_thread_messages(thread: SenderThread):
    """Display all messages in the given SenderThread."""
    print(f"Thread ID: {thread.thread_id}")
    print(f"Assistant ID: {thread.assistant}")
    print(f"Summary: {thread.summary}")
    print("Messages:")

    for message in thread.messages:
        print(f"  Sender: {message.sender}")
        print(f"  Timestamp: {message.timestamp}")
        print(f"  Content: {message.content}")
        print("")

def reorganize_sources(message: str) -> str:
    """
    Extracts sources from the message, cleans them up, and moves them to the end.

    Args:
    message (str): The original message with inline sources.

    Returns:
    str: The message with cleaned sources moved to the end.
    """
    # Extract sources
    sources = re.findall(r"【.*?】", message)

    # Remove sources from the main text
    ans = re.sub(r"【.*?】", '', message)

    if sources:
        # Clean up sources
        cleaned_sources = []
        for source in sources:
            # Remove the opening 【, the number, and the † (cross) character
            cleaned = re.sub(r"【\d+†\s*", "[", source)
            # Replace the closing 】 with ]
            cleaned = cleaned.replace("】", "]")
            cleaned_sources.append(cleaned)

        # Append cleaned sources to the end of the message
        ans = ans.strip() + "\n\nSources:\n" + "\n".join(cleaned_sources)

    return ans

async def generate_answer(sender_phone_number: str,
                          message: str,
                          profile_name: str) -> Tuple[Optional[str], bool]:
    sent_thinking_message = False
    try:
        logger.debug(f"Generating answer for sender {sender_phone_number} with message: {message}")
        user_threads = get_user_threads(sender_phone_number)
        if user_threads is None:
            logger.error(f"Failed to retrieve user_threads for sender {sender_phone_number}")
            return None, sent_thinking_message

        logger.debug(f"Retrieved user_threads: {user_threads}")

        thread = await get_or_create_thread_in_openai(user_threads)
        if thread is None:
            logger.error(f"Failed to get or create thread for sender {sender_phone_number}")
            return None, sent_thinking_message

        logger.debug(f"Using thread: {thread}")

        await submit_message_to_thread(thread, message)

        run, sent_thinking_message = await run_thread(thread, sender_phone_number, profile_name)

        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.thread_id)
            last_ai_message = extract_last_message_content(messages)
            logger.info(f"Generated answer: {last_ai_message}")

            thread.add_message(content=last_ai_message, role="assistant")
            save_user_threads(sender_phone_number, user_threads)
            logger.debug(f"Saved user_threads for {sender_phone_number}")

            last_ai_message = reorganize_sources(last_ai_message)

            return last_ai_message, sent_thinking_message
        else:
            logger.error(f"Run failed with status: {run.status}")
            error_message = "I'm sorry, I couldn't complete the task. Please try asking your question again."
            return error_message, sent_thinking_message

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "I'm sorry, there was an issue with the AI service. Please try again later.", sent_thinking_message

    except Exception as e:
        logger.error(f"Error in generate_answer: {str(e)}", exc_info=True)
        return "An unexpected error occurred. Please try again later.", sent_thinking_message



async def simulate_incoming_message(sender: str, message: str):
    logger.info(f"Received message from {sender}: {message}")
    try:
        response, sent_thinking_message = await generate_answer(sender, message)


        print(f"Sender: {sender}")
        print(f"Response from OpenAI: {response}")
        print(f"Sent thinking message: true or false: {sent_thinking_message}")

        if response:
            if sent_thinking_message:
                await asyncio.sleep(0.1)  # Ensure order of messages
            await send_responses_with_twilio(to=sender, body=response)
        else:
            logger.warning(f"Empty response generated for {sender}")
            if not sent_thinking_message:
                await send_responses_with_twilio(to=f"{sender}", body="I'm sorry, I couldn't generate a response at this time. Please try again later.")
    except Exception as e:
        logger.error(f"Error processing message for {sender}: {str(e)}")
        await send_responses_with_twilio(to=f"whatsapp:{sender}", body="I'm sorry, an error occurred while processing your message. Please try again later.")

async def main():
    # Simulated database
    db = {}

    # Simulate multiple incoming messages
    messages = [
        ("+4917624908925", "Hello, can you help me with a question?"),
        #("+4917624908925", "What's the weather like today?"),
        #("+4917624908925", "Tell me a joke"),
    ]

    # Process messages concurrently
    tasks = [simulate_incoming_message(sender, message) for sender, message in messages]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Ensure environment variables are set
    required_env_vars = ['OPENAI_API_KEY', 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']
    for var in required_env_vars:
        if var not in os.environ:
            raise EnvironmentError(f"{var} is not set in the environment variables")

    asyncio.run(main())