import base64
from auth import api_call

def create_dream(email, character_id, prompt, selected_image_index=0):
    """Create a dream video using character image"""
    result = api_call("create_dream", {
        "email": email,
        "character_id": character_id,
        "prompt": prompt,
        "selected_image_index": selected_image_index
    })
    return result.get("success", False), result.get("dream_id")

def get_dreams(email):
    """Get all dreams for a user"""
    result = api_call("get_dreams", {"email": email})
    if result.get("success"):
        return result.get("dreams", [])
    return []
