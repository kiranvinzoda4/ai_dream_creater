import base64
from auth import api_call

def create_character(email, name, description, image_files):
    """Create a new character with images"""
    images = []
    for img_file in image_files:
        if img_file:
            images.append(base64.b64encode(img_file.read()).decode())
    
    result = api_call("create_character", {
        "email": email,
        "name": name,
        "description": description,
        "images": images
    })
    return result.get("success", False)

def get_characters(email):
    """Get all characters for a user"""
    result = api_call("get_characters", {"email": email})
    if result.get("success"):
        return result.get("characters", [])
    return []

def delete_character(email, character_id):
    """Delete a character"""
    result = api_call("delete_character", {"email": email, "character_id": character_id})
    return result.get("success", False)
