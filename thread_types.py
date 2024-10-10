import json
from datetime import datetime

class Message:
    def __init__(self, role: str, content: str, timestamp: str):
        self.content = content
        self.timestamp = timestamp
        self.role = role

    def __repr__(self):
        return f"Message(role={self.role}, content={self.content}, timestamp={self.timestamp})"

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['role'], data['content'], data['timestamp'])

class SenderThread:
    def __init__(self, thread_id: str, assistant: str, summary: str = "", messages: list = None):
        self.thread_id = thread_id
        self.assistant = assistant
        self.summary = summary
        self.messages = messages if messages is not None else []  # Initialize messages list

    def __repr__(self):
        return f"SenderThread(thread_id={self.thread_id}, assistant={self.assistant}, summary={self.summary}, messages={self.messages})"

    def add_message(self, role: str, content: str):
        """Add a new message to the thread with the current timestamp."""
        timestamp = datetime.now().isoformat()  # Generate the current timestamp in ISO format
        message = Message(role, content, timestamp)
        self.messages.append(message)

    def get_number_of_messages(self) -> int:
        """Return the number of messages in the thread."""
        return len(self.messages)

    def to_dict(self):
        return {
            "thread_id": self.thread_id,
            "assistant": self.assistant,
            "summary": self.summary,
            "messages": [message.to_dict() for message in self.messages]
        }

    @classmethod
    def from_dict(cls, data):
        thread = cls(data['thread_id'], data['assistant'], data['summary'])
        thread.messages = [Message.from_dict(m) for m in data['messages']]
        return thread

class UserThreads:
    def __init__(self, sender_phone_number: str):
        self.sender_phone_number = sender_phone_number
        self.sender_name = "" # set the name if we know it
        self.threads = []  # List to keep track of multiple threads

    def add_thread(self, thread: SenderThread):
        """Add a new thread for the user."""
        self.threads.append(thread)

    def find_thread(self, thread_id: str):
        """Find a thread by its ID."""
        for thread in self.threads:
            if thread.thread_id == thread_id:
                return thread
        return None

    def display_threads_info(self):
        """Display the number of threads and the number of messages in each thread."""
        print(f"User: {self.sender_phone_number}")
        print(f"Total number of threads: {len(self.threads)}")

        for thread in self.threads:
            num_messages = thread.get_number_of_messages()

            # Initialize counters for user and assistant messages based on role
            user_messages = sum(1 for message in thread.messages if message.role == 'user')
            assistant_messages = sum(1 for message in thread.messages if message.role == 'assistant')

            # Debugging output to inspect message roles
            print(f"Debugging message roles in thread {thread.thread_id}:")
            for message in thread.messages:
                print(f"  Message Role: {message.role}, Content: {message.content}")

            print(f"Thread ID: {thread.thread_id} - Number of messages: {num_messages}")
            print(f"  User messages: {user_messages} - Assistant messages: {assistant_messages}")

    def to_dict(self):
        return {
            "sender_phone_number": self.sender_phone_number,
            "sender_name": self.sender_name,
            "threads": [thread.to_dict() for thread in self.threads]
        }

    @classmethod
    def from_dict(cls, data):
        user_threads = cls(data['sender_phone_number'])
        user_threads.sender_name = data['sender_name']
        user_threads.threads = [SenderThread.from_dict(t) for t in data['threads']]
        return user_threads

    def __repr__(self):
        return f"UserThreads(sender_phone_number={self.sender_phone_number}, threads={self.threads})"