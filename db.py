# db.py

USERS_DB = {}

def create_user(email, name, password):
    if email in USERS_DB:
        return False
    
    USERS_DB[email] = {
        "email": email,
        "name": name,
        "password": password,  # (We will add hashing later)
        "characters": [],
        "profile_picture": None
    }
    return True

def get_user(email):
    return USERS_DB.get(email, None)
