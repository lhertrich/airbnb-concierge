from enum import Enum

class MessageType(Enum):
    PROBLEM = "problem"
    QUESTION = "question"
    COMPLAINT = "complaint"
    OTHER = "other"