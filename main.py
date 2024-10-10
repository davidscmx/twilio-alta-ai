import os
import asyncio

from fastapi import FastAPI, Response, BackgroundTasks, Form, Depends
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
async def receive_message(
    background_tasks: BackgroundTasks,
    Body: str = Form(..., alias="Body"),
    From: str = Form(..., alias="From")
):
    """
    Endpoint to receive incoming messages, acknowledge them immediately,
    and process them in the background.
    """
    logger.info(f"Message from {From}: {Body}")
    resp = MessagingResponse()

    # Start background task to process the message
    background_tasks.add_task(process_message, Body, From)

    # Immediately return an empty response to acknowledge receipt
    response = Response(content=str(resp), media_type="application/xml")
    return response

async def process_message(body: str, from_: str):
    """
    Process the message in the background and send the response.
    """
    phone_number = from_.removeprefix("whatsapp:")

    try:
        response, sent_thinking_message = await generate_answer(phone_number, body)

        if response is not None:
            if sent_thinking_message:
                await asyncio.sleep(1)
            await send_responses_with_twilio(to=from_, body=response)
        else:
            logger.error(f"No response generated for {phone_number}")
            await send_responses_with_twilio(to=from_, body="I'm sorry, I couldn't generate a response at this time. Please try again later.")

    except Exception as e:
        logger.error(f"Error processing message for {phone_number}: {str(e)}", exc_info=True)
        await send_responses_with_twilio(to=from_, body="I'm sorry, an error occurred while processing your message. Please try again later.")
