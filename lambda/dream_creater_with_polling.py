import json
import boto3
import os
from datetime import datetime
import uuid
import base64

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
users_table = dynamodb.Table("dream_users")
characters_table = dynamodb.Table("dream_characters")
dreams_table = dynamodb.Table("dream_videos")

s3 = boto3.client("s3", region_name="us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "dream-creator-images")

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
                        continue
                char["image_urls"] = urls

            return response({"success": True, "characters": characters})

        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "create_dream":
        email = body.get("email")
        character_id = body.get("character_id")
        prompt = body.get("prompt")

        if not email or not character_id:
            return response({"error": "Missing fields"}, 400)

        dream_id = str(uuid.uuid4())

        try:
            char_data = characters_table.get_item(Key={"character_id": character_id})
            if "Item" not in char_data:
                return response({"error": "Character not found"}, 404)

            character = char_data["Item"]

            if not character.get("image_urls"):
                return response({"error": "No character images found"}, 400)

            # Use demo video for now
            job_id = ""
            video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            status = "demo"

            dreams_table.put_item(Item={
                "dream_id": dream_id,
                "email": email,
                "character_id": character_id,
                "character_name": character.get("name", "Unknown"),
                "prompt": prompt if prompt else "",
                "video_s3_uri": "",
                "video_url": video_url,
                "status": status,
                "job_id": job_id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            return response({
                "success": True,
                "dream_id": dream_id,
                "video_url": video_url,
                "status": status
            })

        except Exception as e:
            print(f"Dream creation failed: {str(e)}")
            return response({"error": str(e)}, 500)

    elif action == "check_dream_status":
        dream_id = body.get("dream_id")
        
        try:
            dream_item = dreams_table.get_item(Key={"dream_id": dream_id})
            if "Item" not in dream_item:
                return response({"error": "Dream not found"}, 404)
            
            dream = dream_item["Item"]
            return response({"success": True, "dream": dream})
            
        except Exception as e:
            return response({"error": str(e)}, 500)eo_url = s3.generate_presigned_url(
                                "get_object",
                                Params={"Bucket": S3_BUCKET, "Key": video_key},
                                ExpiresIn=3600
                            )
                            
                            # Update dream status
                            dreams_table.update_item(
                                Key={"dream_id": dream_id},
                                UpdateExpression="SET #status = :status, video_url = :url",
                                ExpressionAttributeNames={"#status": "status"},
                                ExpressionAttributeValues={
                                    ":status": "completed",
                                    ":url": video_url
                                }
                            )
                            
                            dream["status"] = "completed"
                            dream["video_url"] = video_url
                    
                    elif job_response["status"] == "Failed":
                        dreams_table.update_item(
                            Key={"dream_id": dream_id},
                            UpdateExpression="SET #status = :status",
                            ExpressionAttributeNames={"#status": "status"},
                            ExpressionAttributeValues={":status": "failed"}
                        )
                        dream["status"] = "failed"
                        
                except Exception as job_error:
                    print(f"Job check failed: {str(job_error)}")
            
            return response({"success": True, "dream": dream})
            
        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "get_dreams":
        email = body.get("email")

        try:
            res = dreams_table.scan(
                FilterExpression="email = :e",
                ExpressionAttributeValues={":e": email}
            )

            return response({"success": True, "dreams": res.get("Items", [])})
            
        except Exception as e:
            return response({"error": str(e)}, 500)

    elif action == "delete_dream":
        dream_id = body.get("dream_id")
        try:
            dreams_table.delete_item(Key={"dream_id": dream_id})
            return response({"success": True})
        except Exception as e:
            return response({"error": str(e)}, 500)

    else:
        return response({"error": "Unknown action"}, 400)