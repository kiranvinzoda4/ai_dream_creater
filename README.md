# 🌙 AI Dream Creator

Clean Streamlit app with tabbed login/register and user profiles.

## Setup

### 1. AWS Lambda Setup
1. Create a Lambda function named `dream_creator`
2. Copy code from `lambda/dream_creater.py` to your Lambda function
3. Create DynamoDB table named `dream_users` with `email` as primary key
4. Enable Function URL for your Lambda function with IAM authentication
5. Create IAM user with Lambda invoke permissions and get access keys

### 2. Frontend Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add:
# - Lambda Function URL
# - AWS Access Key ID
# - AWS Secret Access Key
streamlit run app.py
```

## Features

- Tabbed login/register interface
- User profile dashboard
- Session management
- AWS Lambda + DynamoDB backend
- Clean, modern design