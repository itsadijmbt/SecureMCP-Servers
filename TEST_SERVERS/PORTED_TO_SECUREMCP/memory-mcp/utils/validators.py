def validate_user_id(user_id: str) -> str:
    """Validate user ID format."""
    if user_id is None:
        raise ValueError(
            "user_id must be provided either in the method call or when creating the client"
        )
    return user_id

def validate_message_type(message_type: str) -> str:
    """Validate message type."""
    if message_type not in ["human", "ai"]:
        raise ValueError("message_type must be either 'human' or 'ai'")
    return message_type
