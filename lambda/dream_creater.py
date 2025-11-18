import json
import boto3
import os
from datetime import datetime

# DynamoDB table
dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION", "ap-south-1"))
table = dynamodb.Table("dream_users")


# ---------------------------
# Helpers
# ---------------------------
def response(body, code=200):
    return {
        "statusCode": code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",         # CORS
            "Access-Control-Allow-Headers": "*",        # CORS
            "Access-Control-Allow-Methods": "POST,GET,OPTIONS" # CORS
        }
    }


def hash_password(password):
    # Temporary: plain text for testing
    return password


def check_password(password, hashed):
    # Temporary: plain text comparison
    return password == hashed


# ---------------------------
# Main Lambda Router
# ---------------------------
def lambda_handler(event, context):

    # For preflight (OPTIONS request)
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return response({"message": "OK"}, 200)

    try:
        body = json.loads(event["body"])
    except:
        return response({"error": "Invalid JSON"}, 400)

    action = body.get("action")

    if not action:
        return response({"error": "Missing 'action' field"}, 400)


    # --------------------------------
    # REGISTER
    # --------------------------------
    if action == "register":
        name = body.get("name")
        email = body.get("email")
        password = body.get("password")

        if not name or not email or not password:
            return response({"error": "Missing fields"}, 400)

        # Check existing user
        try:
            check = table.get_item(Key={"email": email})
            if "Item" in check:
                return response({"error": "Email already exists"}, 409)

            hashed = hash_password(password)

            table.put_item(
                Item={
                    "email": email,
                    "name": name,
                    "password": hashed,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "profile_picture": None
                }
            )

            return response({"success": True, "message": "User registered successfully"})
        except Exception as e:
            return response({"error": f"Database error: {str(e)}"}, 500)


    # --------------------------------
    # LOGIN
    # --------------------------------
    elif action == "login":
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            return response({"error": "Missing fields"}, 400)

        try:
            res = table.get_item(Key={"email": email})

            if "Item" not in res:
                return response({"error": "User not found"}, 404)

            user = res["Item"]

            if not check_password(password, user["password"]):
                return response({"error": "Invalid password"}, 401)

            # Don't send hashed password back
            user.pop("password", None)

            return response({"success": True, "user": user})
        except Exception as e:
            return response({"error": f"Database error: {str(e)}"}, 500)


    # --------------------------------
    # GET PROFILE
    # --------------------------------
    elif action == "profile":
        email = body.get("email")

        if not email:
            return response({"error": "Missing email"}, 400)

        try:
            res = table.get_item(Key={"email": email})

            if "Item" not in res:
                return response({"error": "User not found"}, 404)

            user = res["Item"]
            user.pop("password", None)

            return response({"success": True, "user": user})
        except Exception as e:
            return response({"error": f"Database error: {str(e)}"}, 500)


    # --------------------------------
    # FALLBACK
    # --------------------------------
    else:
        return response({"error": f"Unknown action '{action}'"}, 400)
