from pydantic import BaseModel

class MessageSchema(BaseModel):
    Body: str
    From: str

    class Config:
        json_schema_extra = {
            "example": {
                "Body": "Hello, this is a message.",
                "From": "whatsapp:+4917624908925"
            }
        }