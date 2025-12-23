# NAS Deployment Configuration (CPU/OpenVINO)
# Usage: cp .env.nas .env && docker compose up

NODE_ENV=production

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/code_talk_db

# Authentication
JWT_SECRET=your_jwt_secret_change_in_production

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80

# AI Backend - OpenVINO (CPU optimized for NAS)
INFERENCE_URL=http://openvino-engine:8001
AI_GATEWAY_URL=http://shared-ai-gateway:8002

# Deployment type marker
DEPLOYMENT_TYPE=nas-cpu
