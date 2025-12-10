import json
import boto3
import os
from datetime import datetime
import uuid
import base64

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION_NAME", "us-east-1"))
users_table = dynamodb.Table("dream_users")
characters_table = dynamodb.Table("dream_characters")
dreams_table = dynamodb.Table("dream_videos")

# S3 setup - bucket is actually in us-east-1
s3 = boto3.client("s3", region_name="us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "dream-creator-images")

# Bedrock setup
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def response(body, code=200):
    return {
        "statusCode": code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "POST,GET,OPTIONS"
        }
    }


def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return response({"message": "OK"})

    try:
        body = json.loads(event["body"])
    except:
        return response({"error": "Invalid JSON"}, 400)

    action = body.get("action")
    if not action:
        return response({"error": "Missing 'action' field"}, 400)

    if action == "register":
        email = body.get("email")
        name = body.get("name")
        password = body.get("password")

        if not email or not name or not password:
            return response({"error": "Missing fields"}, 400)

        try:
            check = users_table.get_item(Key={"email": email})
            if "Item" in check:
                return response({"error": "Email already exists"}, 409)

            users_table.put_item(Item={
                "email": email,
                "name": name,
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            return response({"success": True})
        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "login":
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            return response({"error": "Missing fields"}, 400)

        try:
            user_item = users_table.get_item(Key={"email": email})
            if "Item" not in user_item:
                return response({"error": "User not found"}, 404)

            user = user_item["Item"]
            if user["password"] != password:
                return response({"error": "Invalid password"}, 401)

            user.pop("password", None)
            return response({"success": True, "user": user})

        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "create_character":
        email = body.get("email")
        name = body.get("name")
        description = body.get("description", "")
        images = body.get("images", [])

        if not email or not name:
            return response({"error": "Missing fields"}, 400)

        try:
            char_id = str(uuid.uuid4())
            uploaded_keys = []

            for i, img_b64 in enumerate(images[:3]):
                raw = base64.b64decode(img_b64)
                key = f"characters/{email}/{char_id}/img_{i}.jpg"

                s3.put_object(Bucket=S3_BUCKET, Key=key, Body=raw, ContentType="image/jpeg")
                uploaded_keys.append(key)

            characters_table.put_item(Item={
                "character_id": char_id,
                "email": email,
                "name": name,
                "description": description,
                "image_urls": uploaded_keys,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            return response({"success": True, "character_id": char_id})

        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "get_characters":
        email = body.get("email")

        try:
            res = characters_table.scan(
                FilterExpression="email = :e",
                ExpressionAttributeValues={":e": email}
            )

            characters = res.get("Items", [])
            for char in characters:
                urls = []
                for key in char.get("image_urls", []):
                    try:
                        url = s3.generate_presigned_url(
                            "get_object",
                            Params={"Bucket": S3_BUCKET, "Key": key},
                            ExpiresIn=3600
                        )
                        urls.append(url)
                    except Exception as e:
                        print(f"Error generating presigned URL for {key}: {str(e)}")
                        # Skip broken URLs
                        continue
                char["image_urls"] = urls

            return response({"success": True, "characters": characters})

        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "create_dream":
        email = body.get("email")
        character_id = body.get("character_id")
        prompt = body.get("prompt")

        if not email or not character_id or not prompt:
            return response({"error": "Missing fields"}, 400)

        dream_id = str(uuid.uuid4())

        try:
            char_data = characters_table.get_item(Key={"character_id": character_id})
            if "Item" not in char_data:
                return response({"error": "Character not found"}, 404)

            character = char_data["Item"]

            if not character.get("image_urls"):
                return response({"error": "No character images found"}, 400)

            # Get character image
            img_key = character["image_urls"][0]
            img_obj = s3.get_object(Bucket=S3_BUCKET, Key=img_key)
            img_raw = img_obj["Body"].read()
            img_b64 = base64.b64encode(img_raw).decode("utf-8")

            # Nova Reel request (cross-region call to us-east-1)
            nova_body = {
                "inputText": prompt,
                "images": [
                    {
                        "format": "image/jpeg",
                        "source": "base64",
                        "data": img_b64
                    }
                ],
                "video_generation_config": {
                    "durationSeconds": 2,
                    "dimension": "640x360",
                    "fps": 12
                }
            }

            response_nova = bedrock.invoke_model(
                modelId="amazon.nova-reel-v1:0",
                body=json.dumps(nova_body),
                contentType="application/json",
                accept="application/json"
            )

            response_json = json.loads(response_nova["body"].read())
            video_s3_uri = response_json.get("outputVideo")

            if not video_s3_uri:
                raise Exception("outputVideo missing in response")

            # Extract bucket + key from S3 URI
            bucket_name, key_path = video_s3_uri.replace("s3://", "").split("/", 1)

            # Generate presigned URL
            video_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key_path},
                ExpiresIn=3600
            )
            status = "completed"

            dreams_table.put_item(Item={
                "dream_id": dream_id,
                "email": email,
                "character_id": character_id,
                "character_name": character.get("name", "Unknown"),
                "prompt": prompt,
                "video_s3_uri": video_s3_uri,
                "video_url": video_url,
                "status": status,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            return response({
                "success": True,
                "dream_id": dream_id,
                "video_url": video_url,
                "status": status
            })

        except Exception as e:
            print("Nova Reel failed:", str(e))
            
            # Fallback to sample video
            video_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4"
            status = "sample"

            dreams_table.put_item(Item={
                "dream_id": dream_id,
                "email": email,
                "character_id": character_id,
                "character_name": character.get("name", "Unknown"),
                "prompt": prompt,
                "video_url": video_url,
                "status": status,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            return response({
                "success": True,
                "dream_id": dream_id,
                "video_url": video_url,
                "status": status
            })

    elif action == "get_dreams":
        email = body.get("email")

        res = dreams_table.scan(
            FilterExpression="email = :e",
            ExpressionAttributeValues={":e": email}
        )

        return response({"success": True, "dreams": res["Items"]})

    elif action == "delete_dream":
        dream_id = body.get("dream_id")
        dreams_table.delete_item(Key={"dream_id": dream_id})
        return response({"success": True})

    else:
        return response({"error": "Unknown action"}, 400)