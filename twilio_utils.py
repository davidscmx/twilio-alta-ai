import asyncio
import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from schemas import MessageSchema

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = Client(account_sid, auth_token)

TWILIO_NUMBER = 'whatsapp:+5216143827784'

ADMIN_NUMBERS = [
    'whatsapp:+4917624908925',
    'whatsapp:+5216143827784',
]

def split_message(text, max_length=1000):
    paragraphs = text.split('\n')

    messages = []  # List to store optimized text chunks
    current_chunk = ""

    for para in paragraphs:
        # Adding this paragraph does not exceed max_length

        if len(current_chunk) + len(para) + 1 <= max_length:
            current_chunk += para + "\n"  # Use a single newline for spacing

        else:
            # If the current chunk is too long, start a new one
            if current_chunk:
                messages.append(current_chunk.rstrip())
            current_chunk = para + "\n"

    # Don't forget to add the last chunk, ensuring to remove trailing newline
    if current_chunk:
        messages.append(current_chunk.rstrip())

    return messages


def correct_format(texto):
  # Reemplaza asteriscos dobles con uno solo
  corrected_text = texto.replace("**", "*")
  return corrected_text


async def send_responses_with_twilio(to: str, body: str):
    MAX_SMS_LENGTH = 1000
    messages = split_message(body, MAX_SMS_LENGTH)

    # Ensure the 'to' number is in the correct format for WhatsApp
    if not to.startswith('whatsapp:'):
        to = f'whatsapp:{to}'  # Add the '+' sign if it's not already there

    print(f"Sending messages from {TWILIO_NUMBER} to {to}")
    for msg in messages:

        msg = correct_format(msg)
        message = twilio_client.messages.create(
                                          from_=TWILIO_NUMBER,
                                          body=msg,
                                          to=to)

        print(f"Message SID {message.sid}: {message.body} Sent to {to}")
        print(f"Message Status: {message.status}")
        print(f"Error Code: {message.error_code}")
        print(f"Error Message: {message.error_message}")
