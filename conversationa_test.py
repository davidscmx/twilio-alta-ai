from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import time
import os
# Your Twilio account credentials
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# Create a new conversation
def create_conversation(friendly_name):
    try:
        conversation = client.conversations.v1.conversations.create(
            friendly_name=friendly_name
        )
        print(f"Conversation created with SID: {conversation.sid}")
        return conversation
    except TwilioRestException as e:
        print(f"Error creating conversation: {e}")
        return None

# Add a participant to the conversation
def add_participant(conversation_sid, participant_address):
    try:
        # First, check if the participant already exists
        participants = client.conversations.v1.conversations(conversation_sid) \
            .participants.list(limit=20)

        for participant in participants:
            if participant.messaging_binding['address'] == participant_address:
                print(f"Participant {participant_address} already exists in the conversation.")
                return participant

        # If not found, add the new participant
        participant = client.conversations.v1.conversations(conversation_sid) \
            .participants.create(
                messaging_binding_address=participant_address,
                messaging_binding_proxy_address='whatsapp:+5216143827784'
            )
        print(f"Participant added with SID: {participant.sid}")
        return participant
    except TwilioRestException as e:
        print(f"Error adding participant: {e}")

# Send a typing indicator
def send_typing_indicator(conversation_sid):
    try:
        client.conversations.v1.conversations(conversation_sid) \
            .messages.create(
                body='',
                attributes='{"typing": {"type": "started"}}'
            )
        print("Typing indicator sent")
    except TwilioRestException as e:
        print(f"Error sending typing indicator: {e}")

# Send a message
def send_message(conversation_sid, body):
    try:
        message = client.conversations.v1.conversations(conversation_sid) \
            .messages.create(author='AI Assistant', body=body)
        print(f"Message sent with SID: {message.sid}")
    except TwilioRestException as e:
        print(f"Error sending message: {e}")

# Remove all participants from a conversation
def remove_all_participants(conversation_sid):
    try:
        participants = client.conversations.v1.conversations(conversation_sid) \
            .participants.list(limit=50)

        for participant in participants:
            client.conversations.v1.conversations(conversation_sid) \
                .participants(participant.sid).delete()
        print("All participants removed from the conversation.")
    except TwilioRestException as e:
        print(f"Error removing participants: {e}")

# Main function to demonstrate the flow
def main():
    # Create a new conversation
    conversation = create_conversation(f"AI Assistant Chat {time.time()}")  # Use timestamp for unique name
    if not conversation:
        return

    # Add a participant (replace with actual WhatsApp number)
    add_participant(conversation.sid, 'whatsapp:+4917624908925')

    # Simulate AI processing with typing indicator
    send_typing_indicator(conversation.sid)
    time.sleep(2)  # Simulate processing time

    # Send a message
    send_message(conversation.sid, "Hello! How can I assist you today?")

if __name__ == "__main__":
    main()