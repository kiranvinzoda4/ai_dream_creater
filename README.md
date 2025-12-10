# 🌙 AI Dream Creator

> **Transform your imagination into reality with AI-powered video generation**

A full-stack web application that leverages **Amazon Bedrock's Nova Reel** model to create personalized dream videos from character images and text prompts. Built with modern cloud architecture and intuitive user experience.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=for-the-badge&logo=amazon-dynamodb&logoColor=white)](https://aws.amazon.com/dynamodb/)

## 🚀 Features

### 🎯 Core Functionality
- **AI Video Generation**: Create 2-second dream videos using Amazon Nova Reel model
- **Character Management**: Upload and manage up to 3 images per character
- **User Authentication**: Secure login/register system with session management
- **Dream History**: Track and replay all generated videos
- **Real-time Processing**: Live status updates during video generation

### 🏗️ Technical Highlights
- **Serverless Architecture**: AWS Lambda + DynamoDB for scalable backend
- **Cloud Storage**: S3 with presigned URLs for secure image handling
- **Cross-Region Integration**: Optimized for Nova Reel availability in us-east-1
- **Modern Frontend**: Clean Streamlit interface with tabbed navigation
- **Cost Optimization**: Low-resolution settings (360p, 12fps) for minimal charges

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Interactive web interface
- **Python** - Core application logic
- **Session Management** - User state persistence

### Backend & Cloud
- **AWS Lambda** - Serverless compute
- **Amazon DynamoDB** - NoSQL database (3 tables)
- **Amazon S3** - Object storage with presigned URLs
- **Amazon Bedrock** - Nova Reel model integration
- **AWS IAM** - Security and permissions

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│   AWS Lambda     │───▶│  Amazon Bedrock │
│   Frontend      │    │   (us-east-1)    │    │   Nova Reel     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌──────────────────┐             │
         │              │   Amazon S3      │             │
         │              │  Image Storage   │             │
         │              └──────────────────┘             │
         │                       │                       │
         └───────────────────────▼───────────────────────┘
                        ┌──────────────────┐
                        │   DynamoDB       │
                        │ Users/Characters │
                        │    /Dreams       │
                        └──────────────────┘
```

## 📊 Database Schema

### Users Table (`dream_users`)
```json
{
  "email": "user@example.com",     // Primary Key
  "name": "John Doe",
  "password": "hashed_password",
  "created_at": "2024-01-15 10:30"
}
```

### Characters Table (`dream_characters`)
```json
{
  "character_id": "uuid-string",   // Primary Key
  "email": "user@example.com",
  "name": "Character Name",
  "description": "Character description",
  "image_urls": ["s3://bucket/key1", "s3://bucket/key2"],
  "created_at": "2024-01-15 10:30"
}
```

### Dreams Table (`dream_videos`)
```json
{
  "dream_id": "uuid-string",       // Primary Key
  "email": "user@example.com",
  "character_id": "uuid-string",
  "prompt": "walking in forest",
  "video_s3_uri": "s3://bucket/video.mp4",
  "video_url": "presigned-url",
  "status": "completed",
  "created_at": "2024-01-15 10:30"
}
```

## 🎥 Demo Workflow

1. **User Registration/Login** → Secure authentication with DynamoDB
2. **Character Creation** → Upload images, store in S3 with metadata
3. **Dream Generation** → Select character + prompt → Nova Reel processing
4. **Video Delivery** → S3 presigned URLs for secure video access
5. **History Management** → Track all dreams with replay functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account with appropriate permissions
- Streamlit

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-dream-creator.git
cd ai-dream-creator
```

2. **Set up virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your AWS credentials and Lambda URL
```

5. **Run the application**
```bash
streamlit run app.py
```

## ⚙️ AWS Setup

### 1. DynamoDB Tables
```bash
# Users table
aws dynamodb create-table --table-name dream_users --attribute-definitions AttributeName=email,AttributeType=S --key-schema AttributeName=email,KeyType=HASH --billing-mode PAY_PER_REQUEST

# Characters table  
aws dynamodb create-table --table-name dream_characters --attribute-definitions AttributeName=character_id,AttributeType=S --key-schema AttributeName=character_id,KeyType=HASH --billing-mode PAY_PER_REQUEST

# Dreams table
aws dynamodb create-table --table-name dream_videos --attribute-definitions AttributeName=dream_id,AttributeType=S --key-schema AttributeName=dream_id,KeyType=HASH --billing-mode PAY_PER_REQUEST
```

### 2. S3 Bucket
```bash
aws s3 mb s3://your-dream-creator-images --region us-east-1
```

### 3. Lambda Function
- Deploy `lambda/dream_creater.py` to AWS Lambda
- Set runtime to Python 3.9+
- Configure environment variables
- Enable Function URL with IAM authentication

### 4. IAM Permissions
Required permissions for Lambda execution role:
- `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:Scan`, `dynamodb:DeleteItem`
- `s3:GetObject`, `s3:PutObject`, `s3:GeneratePresignedUrl`
- `bedrock:InvokeModel` for Nova Reel access

## 💡 Key Technical Decisions

### Cost Optimization
- **Low-resolution videos** (360p, 12fps, 2sec) to minimize Bedrock charges
- **Presigned URLs** instead of public S3 buckets for security
- **Pay-per-request** DynamoDB billing for variable usage

### Performance
- **Cross-region optimization** for Nova Reel availability
- **Base64 encoding** for efficient image transfer
- **Error handling** with fallback mechanisms

### Security
- **IAM-based authentication** for Lambda Function URLs
- **Private S3 buckets** with time-limited access
- **Input validation** and sanitization

## 📈 Scalability Features

- **Serverless architecture** - Auto-scaling based on demand
- **NoSQL database** - Handles variable workloads efficiently  
- **Cloud storage** - Unlimited capacity for user content
- **Regional deployment** - Can be deployed across multiple AWS regions

## 🔮 Future Enhancements

- [ ] **Advanced AI Models** - Integration with additional Bedrock models
- [ ] **Video Editing** - Post-processing capabilities
- [ ] **Social Features** - Share dreams with other users
- [ ] **Mobile App** - React Native or Flutter implementation
- [ ] **Analytics Dashboard** - Usage metrics and insights

## 📝 Environment Variables

```env
LAMBDA_URL=https://your-lambda-url.lambda-url.us-east-1.on.aws/
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET=your-dream-creator-images
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Amazon Web Services** for providing robust cloud infrastructure
- **Streamlit** for the intuitive web framework
- **Amazon Bedrock** for cutting-edge AI capabilities

---

**Built with ❤️ by [Kiran Vinzoda]** 