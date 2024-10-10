import os
import asyncio

from fastapi import FastAPI, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from assistant import generate_answer
import logging


from schemas import MessageSchema
from twilio_utils import send_responses_with_twilio


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


IS_REPLIT = 'REPLIT_USER' in os.environ

if IS_REPLIT:
    from replit import db
else:
    db = {}

origins = []
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello World!"}

@app.post("/incoming_assistant/")
async def receive_message(background_tasks: BackgroundTasks, message: MessageSchema):
    """
    Endpoint to receive incoming messages, acknowledge them immediately,
    and process them in the background.
    """
    print(f"Message from {message.From}: {message.Body}")

    resp = MessagingResponse()

    # Start background task to process the message
    background_tasks.add_task(process_message, message)

    # Immediately return an empty response to acknowledge receipt
    # and avoid Twilio's timeout
    response = Response(content=str(resp), media_type="application/xml")
    return response

async def process_message(message: MessageSchema):
    """
    Process the message in the background and send the response.
    """
    phone_number = message.From.removeprefix("whatsapp:")

    try:
        response, sent_thinking_message = await generate_answer(phone_number, message.Body)

        if response:
            if sent_thinking_message:
                await asyncio.sleep(1)
            await send_responses_with_twilio(to=message.From, body=response)
        else:
            logger.warning(f"Empty response generated for {phone_number}")
            if not sent_thinking_message:
                await send_responses_with_twilio(to=message.From, body="I'm sorry, I couldn't generate a response at this time. Please try again later.")

    except Exception as e:
        logger.error(f"Error processing message for {phone_number}: {str(e)}")
        await send_responses_with_twilio(to=message.From, body="I'm sorry, an error occurred while processing your message. Please try again later.")
