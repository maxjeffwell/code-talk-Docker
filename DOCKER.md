# Docker Deployment Guide

This guide explains how to run the code-talk application using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Database Management](#database-management)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Useful Commands](#useful-commands)

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### Install Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
```bash
brew install --cask docker
# Or download from https://www.docker.com/products/docker-desktop
```

#### Windows
Download Docker Desktop from https://www.docker.com/products/docker-desktop

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Architecture

The code-talk application consists of five containerized services:

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                      │
│            Reverse Proxy & Load Balancer                │
└───────────────┬─────────────────────────┬───────────────┘
                │                         │
        ┌───────▼────────┐       ┌────────▼──────┐
        │  GraphQL Server │       │ React Client  │
        │   (Port 8000)   │       │  (Port 5000)  │
        │  Apollo + Express│       │  React SPA    │
        └───────┬─────────┘       └───────────────┘
                │
        ┌───────▼────────┐       ┌────────────────┐
        │   PostgreSQL   │       │     Redis      │
        │   (Port 5432)  │       │  (Port 6379)   │
        │   Database     │       │  Cache/PubSub  │
        └────────────────┘       └────────────────┘
```

### Services

1. **nginx**: Reverse proxy routing requests to server and client
2. **server**: Apollo GraphQL API with Express.js (Node 20)
3. **client**: React SPA served by Express (Node 18)
4. **postgres**: PostgreSQL 16 database
5. **redis**: Redis 7 for caching and real-time subscriptions

### Network

All services communicate on an internal bridge network: `code-talk-network`

### Volumes

- `postgres_data`: Persistent PostgreSQL database storage
- `redis_data`: Persistent Redis data storage

## Quick Start

### 1. Clone and Navigate
```bash
cd /home/maxjeffwell/GitHub_Projects/code-talk
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
vim .env
```

### 3. Start Services
```bash
# Development (uses Docker Hub images)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access Application
- **Frontend**: http://localhost
- **GraphQL API**: http://localhost/graphql
- **GraphQL Playground**: http://localhost:8000/graphql (if enabled)
- **Health Check**: http://localhost/health

### 5. Stop Services
```bash
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

## Development Setup

### Using Docker Hub Images (Recommended)

The default `docker-compose.yml` uses pre-built images from Docker Hub:
- `maxjeffwell/code-talk-graphql-server:latest`
- `maxjeffwell/code-talk-graphql-client:latest`

```bash
# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# View real-time logs
docker-compose logs -f server
docker-compose logs -f client
```

### Building Locally

To build from source instead of using Docker Hub images:

```bash
# Build images
docker-compose build

# Start with rebuild
docker-compose up -d --build

# Or build specific service
docker-compose build server
docker-compose build client
```

### Development with Hot Reload

For active development, you can use development stage Dockerfiles with volume mounts:

```yaml
# Create docker-compose.dev.yml
services:
  server:
    build:
      context: ./code-talk-graphql-server
      target: development
    volumes:
      - ./code-talk-graphql-server/src:/app/src
    command: npm run dev

  client:
    build:
      context: ./code-talk-graphql-client
      target: development
    volumes:
      - ./code-talk-graphql-client/src:/app/src
    ports:
      - "3000:3000"  # React dev server
    command: npm run dev
```

Then run:
```bash
docker-compose -f docker-compose.dev.yml up
```

## Production Setup

### 1. Create Production Environment File
```bash
cp .env.production.example .env.production
```

### 2. Configure Production Variables
Edit `.env.production` and set:
- Strong `POSTGRES_PASSWORD` (16+ characters)
- Strong `REDIS_PASSWORD` (16+ characters)
- Strong `JWT_SECRET` (64+ characters)
- Your production domain in `ALLOWED_ORIGINS`
- Production GraphQL endpoints

**Generate secure secrets:**
```bash
# Generate JWT secret (64 characters)
openssl rand -base64 64

# Generate database password
openssl rand -base64 32
```

### 3. Deploy Production Stack
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### 4. Monitor Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Features

The production setup includes:
- **Resource Limits**: CPU and memory constraints
- **Security Hardening**: Read-only filesystems, no-new-privileges
- **Health Checks**: Automatic container restart on failure
- **Log Rotation**: Prevents disk space issues
- **Auto-restart**: `restart: unless-stopped` policy

## Database Management

### Initial Setup

The PostgreSQL database will be automatically initialized on first run. The server will create tables using Sequelize models.

### Seed Data

To populate the database with initial data:

```bash
# Shell into server container
docker-compose exec server /bin/sh

# Run seeders
npm run seed

# Or seed with force (drop existing data)
npm run seed:force

# Seed specific data (e.g., rooms)
npm run seed:rooms

# Exit container
exit
```

### Database Migrations

If you need to run Sequelize migrations:

```bash
docker-compose exec server npm run migrate
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres code_talk_db > backup.sql

# Or with gzip compression
docker-compose exec postgres pg_dump -U postgres code_talk_db | gzip > backup.sql.gz
```

### Restore Database

```bash
# From SQL file
docker-compose exec -T postgres psql -U postgres code_talk_db < backup.sql

# From gzipped file
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U postgres code_talk_db
```

### Access PostgreSQL CLI

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres code_talk_db

# Run queries
SELECT * FROM "Users";
\dt    # List tables
\q     # Quit
```

### Access Redis CLI

```bash
# Connect to Redis
docker-compose exec redis redis-cli -a your_redis_password

# Redis commands
PING
KEYS *
GET key_name
QUIT
```

## Configuration

### Environment Variables

#### Development (.env)
```env
NODE_ENV=development
POSTGRES_DB=code_talk_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
REDIS_PASSWORD=redis_password
JWT_SECRET=your_jwt_secret_change_in_production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80
REACT_APP_GRAPHQL_HTTP_URI=http://localhost/graphql
REACT_APP_GRAPHQL_WS_URI=ws://localhost/graphql
```

#### Production (.env.production)
```env
NODE_ENV=production
POSTGRES_DB=code_talk_production
POSTGRES_USER=code_talk_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
REDIS_PASSWORD=STRONG_PASSWORD_HERE
JWT_SECRET=LONG_RANDOM_SECRET_64_PLUS_CHARS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REACT_APP_GRAPHQL_HTTP_URI=https://yourdomain.com/graphql
REACT_APP_GRAPHQL_WS_URI=wss://yourdomain.com/graphql
VERSION=v1.0.0
```

### Port Mappings

Default port mappings (can be changed in docker-compose.yml):
- `80` → nginx
- `5000` → client
- `8000` → server
- `5432` → postgres
- `6379` → redis

To use different host ports:
```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Access on http://localhost:8080
```

### Resource Limits

In production, services have resource limits:

| Service | CPU Limit | Memory Limit |
|---------|-----------|--------------|
| server | 1.0 core | 1GB |
| client | 0.5 core | 512MB |
| postgres | 1.0 core | 1GB |
| redis | 0.5 core | 512MB |
| nginx | 0.5 core | 256MB |

Adjust in `docker-compose.prod.yml` under `deploy.resources`.

## Troubleshooting

### Container Won't Start

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs server
docker-compose logs client

# Check detailed container info
docker inspect code-talk-graphql-server
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose exec postgres pg_isready -U postgres

# Check database logs
docker-compose logs postgres

# Verify connection string
docker-compose exec server env | grep DATABASE_URL

# Test connection from server
docker-compose exec server node -e "require('pg').Client({connectionString:process.env.DATABASE_URL}).connect().then(()=>console.log('OK'))"
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose exec redis redis-cli -a your_password PING

# View Redis logs
docker-compose logs redis

# Test connection
docker-compose exec server node -e "require('ioredis')({host:'redis',port:6379,password:process.env.REDIS_PASSWORD}).ping().then(console.log)"
```

### GraphQL Server Not Responding

```bash
# Check health endpoint
curl http://localhost/health

# Check server logs
docker-compose logs -f server

# Verify server is listening
docker-compose exec server netstat -tuln | grep 8000

# Check nginx routing
docker-compose logs nginx
```

### Client Build Failures

```bash
# Check build logs
docker-compose logs client

# Rebuild client
docker-compose build --no-cache client

# Check environment variables
docker-compose exec client env | grep REACT_APP
```

### Port Already in Use

```bash
# Find process using port 80
sudo lsof -i :80

# Kill process
sudo kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Out of Disk Space

```bash
# Remove unused containers, images, volumes
docker system prune -a --volumes

# Check disk usage
docker system df

# Remove specific volumes
docker volume ls
docker volume rm code-talk_postgres_data
```

### Permission Denied Errors

```bash
# Fix volume permissions
docker-compose exec server chown -R nodejs:nodejs /app

# Or rebuild with --no-cache
docker-compose build --no-cache
```

## Useful Commands

### Container Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d server

# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop server

# Restart service
docker-compose restart server

# Remove containers (keeps volumes)
docker-compose down

# Remove containers and volumes (WARNING: deletes data!)
docker-compose down -v
```

### Logs and Monitoring

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Logs for specific service
docker-compose logs -f server

# Last 100 lines
docker-compose logs --tail=100 server

# Logs since 1 hour ago
docker-compose logs --since 1h server
```

### Execute Commands in Containers

```bash
# Shell into container
docker-compose exec server /bin/sh
docker-compose exec client /bin/sh

# Run command without shell
docker-compose exec server npm run seed

# Run as specific user
docker-compose exec --user nodejs server npm run seed
```

### Image Management

```bash
# Pull latest images from Docker Hub
docker-compose pull

# Build images locally
docker-compose build

# Build without cache
docker-compose build --no-cache

# Push images to Docker Hub (requires authentication)
docker-compose push
```

### Health Checks

```bash
# Check container health
docker-compose ps

# Inspect health status
docker inspect --format='{{json .State.Health}}' code-talk-graphql-server | jq

# Manual health check
curl http://localhost/health
```

### Database Operations

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres code_talk_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U postgres code_talk_db < backup.sql

# Drop and recreate database
docker-compose exec postgres psql -U postgres -c "DROP DATABASE code_talk_db;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE code_talk_db;"
```

### Network Debugging

```bash
# List networks
docker network ls

# Inspect network
docker network inspect code-talk_code-talk-network

# Test connectivity between services
docker-compose exec server ping postgres
docker-compose exec server ping redis
```

## Heroku Integration

Your existing Heroku deployment will continue to work independently. The Docker setup doesn't interfere with:
- Heroku Procfiles
- Heroku buildpacks
- Heroku environment variables
- Heroku PostgreSQL/Redis add-ons

Both can run in parallel:
- **Heroku**: Production deployment (current)
- **Docker**: Local development, testing, future K8s deployment

## Next Steps

1. **Local Development**: Use Docker Compose for consistent dev environment
2. **CI/CD**: GitHub Actions build and push images automatically
3. **Kubernetes**: Deploy to production Kubernetes cluster (see KUBERNETES.md)
4. **Monitoring**: Add Prometheus/Grafana for metrics
5. **Backups**: Automate database backups

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [CI/CD Guide](./CICD.md)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs: `docker-compose logs -f`
3. Open an issue on GitHub
