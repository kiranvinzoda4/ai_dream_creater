import requests
import os
import json
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import boto3

load_dotenv()

API_URL = os.getenv("LAMBDA_URL")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

def api_call(action, data={}):
    if not API_URL:
        return {"error": "Lambda URL not configured"}
    
    try:
        data["action"] = action
        
        # Try with AWS authentication if credentials are provided
        if AWS_ACCESS_KEY and AWS_SECRET_KEY:
            json_data = json.dumps(data)
            
            session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
            credentials = session.get_credentials()
            
            request = AWSRequest(
                method='POST', 
                url=API_URL, 
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            SigV4Auth(credentials, 'lambda', AWS_REGION).add_auth(request)
            
            r = requests.post(API_URL, data=json_data, headers=dict(request.headers))
        else:
            # Fallback to simple POST (if Lambda URL is public)
            r = requests.post(API_URL, json=data)
        
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 502:
            return {"error": "Lambda function error - check function logs"}
        
        if r.text.strip() == "Internal Server Error":
            return {"error": "Lambda internal error - check function configuration"}
            
        return r.json()
        
    except json.JSONDecodeError:
        return {"error": "Invalid response from server"}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"error": f"Connection failed: {str(e)}"}

def register_user(name, email, password):
    result = api_call("register", {"name": name, "email": email, "password": password})
    print(f"Register API response: {result}")  # Debug
    return result.get("success", False)

def authenticate(email, password):
    result = api_call("login", {"email": email, "password": password})
    print(f"Login API response: {result}")  # Debug
    if result.get("success"):
        return result.get("user")
    return None
