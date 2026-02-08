# code-talk

## Build Status

**Server (Apollo GraphQL API)**
- [![CI](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/ci.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/ci.yml) Continuous Integration
- [![Docker](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/docker-build-push.yml) Docker Build & Push

**Client (React SPA)**
- [![CI](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/ci.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/ci.yml) Continuous Integration
- [![Docker](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/docker-build-push.yml) Docker Build & Push

---

A real-time collaborative coding platform with GraphQL API, built with React, Apollo, PostgreSQL, and Redis.

## Architecture

This is a monorepo containing two separate applications:

- **[code-talk-graphql-server](./code-talk-graphql-server/)**: Apollo GraphQL API server (Node.js + Express + PostgreSQL + Redis)
- **[code-talk-graphql-client](./code-talk-graphql-client/)**: React single-page application (React 18 + Apollo Client)

## Tech Stack

### Backend
- Apollo Server 3.13.0
- Express.js
- PostgreSQL with Sequelize ORM
- Redis (caching & pub/sub for real-time features)
- GraphQL with WebSocket subscriptions
- JWT Authentication
- DataLoader for efficient data fetching

### Frontend
- React 18.3.1
- Apollo Client 3.13.8
- GraphQL WebSocket (graphql-ws)
- React Router 6.30.1
- styled-components
- Real-time collaboration features

## Quick Start

### Local Development (Without Docker)

1. **Setup Server**
   ```bash
   cd code-talk-graphql-server
   npm install
   cp .env.example .env  # Configure PostgreSQL, Redis, and JWT secret
   npm run dev
   ```

2. **Setup Client**
   ```bash
   cd code-talk-graphql-client
   npm install
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - GraphQL API: http://localhost:8000/graphql

### Docker Deployment

Run the entire stack with Docker (includes PostgreSQL and Redis):

```bash
# Development
docker-compose up -d

# Production
cp .env.production.example .env.production  # Configure production values
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

See [DOCKER.md](./DOCKER.md) for detailed Docker deployment instructions.

## Deployment

### Production (Kubernetes)

The application runs on a self-hosted **K3s cluster** managed via ArgoCD GitOps:

- **Live:** [code-talk.el-jefe.me](https://code-talk.el-jefe.me)
- **Ingress:** Traefik with automatic TLS via cert-manager + Let's Encrypt
- **Secrets:** Doppler + External Secrets Operator
- **CI/CD:** GitHub Actions → Docker Hub → ArgoCD auto-sync
- **Helm:** Deployed via shared `portfolio-common` library chart

## Project Structure

```
code-talk/
├── code-talk-graphql-server/    # Backend API
│   ├── src/
│   │   ├── models/              # Sequelize models (User, Message, Room)
│   │   ├── schema/              # GraphQL schemas
│   │   ├── resolvers/           # GraphQL resolvers
│   │   ├── loaders/             # DataLoader instances
│   │   ├── config/              # Database & Redis config
│   │   └── index.js             # Server entry point
│   ├── Dockerfile
│   └── package.json
│
├── code-talk-graphql-client/    # Frontend SPA
│   ├── src/
│   │   ├── components/          # React components
│   │   └── index.js             # App entry point
│   ├── Dockerfile
│   └── package.json
│
├── nginx/                       # Nginx reverse proxy config
│   └── nginx.conf
│
├── docker-compose.yml           # Development Docker setup
├── docker-compose.prod.yml      # Production Docker setup
├── .env                         # Development environment variables
├── .env.production.example      # Production environment template
├── DOCKER.md                    # Docker deployment guide
├── CICD.md                      # CI/CD pipeline guide
└── README.md                    # This file
```

## Features

### Authentication & Authorization
- JWT-based authentication
- Secure password hashing with bcrypt
- Protected GraphQL resolvers

### Real-time Collaboration
- WebSocket subscriptions for live updates
- Redis pub/sub for message distribution
- Multi-user collaborative coding rooms

### API Features
- GraphQL API with Apollo Server
- DataLoader for efficient batch loading and N+1 prevention
- Health check endpoints
- CORS configuration
- Rate limiting and security middleware
- GraphQL depth and complexity limiting

### Frontend Features
- Responsive UI with styled-components
- Client-side routing with React Router
- Real-time updates with Apollo Client subscriptions
- WebSocket connection management
- Session management

## Development

### Server Development

```bash
cd code-talk-graphql-server
npm run dev          # Start dev server with hot reload
npm test             # Run tests
npm run seed         # Seed database with test data
npm run seed:drop    # Drop and reseed database
```

### Client Development

```bash
cd code-talk-graphql-client
npm run dev          # Start dev server (port 3000)
npm run build        # Create production build
npm run lint         # Run ESLint
npm test             # Run tests
```

## Environment Variables

### Server
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret for JWT signing
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_PASSWORD`: Redis password
- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (default: 8000)
- `ALLOWED_ORIGINS`: CORS allowed origins

### Client
- `REACT_APP_GRAPHQL_HTTP_URI`: GraphQL HTTP endpoint
- `REACT_APP_GRAPHQL_WS_URI`: GraphQL WebSocket endpoint

## CI/CD

The project includes automated CI/CD pipelines with GitHub Actions:

- **Continuous Integration**: Automated testing, linting, and build verification
- **Docker Hub**: Automatic image builds and publishing
- **Security Scanning**: Trivy vulnerability scanning
- **Multi-Platform**: Images built for linux/amd64 and linux/arm64

### Docker Hub Images

Pre-built images are available:
- Server: `maxjeffwell/code-talk-graphql-server`
- Client: `maxjeffwell/code-talk-graphql-client`

```bash
docker pull maxjeffwell/code-talk-graphql-server:latest
docker pull maxjeffwell/code-talk-graphql-client:latest
```

## Documentation

- [Docker Deployment Guide](./DOCKER.md) - Run with Docker Compose
- [CI/CD Pipeline Guide](./CICD.md) - GitHub Actions setup
- [Server Documentation](./code-talk-graphql-server/README.md)
- [Client Documentation](./code-talk-graphql-client/README.md)

## Database

### PostgreSQL Models
- **User**: User accounts with authentication
- **Message**: Chat messages in rooms
- **Room**: Collaborative coding/chat spaces

### Database Management

```bash
# Using Docker
docker-compose exec server npm run seed

# Local development
cd code-talk-graphql-server
npm run seed         # Populate with test data
npm run seed:force   # Force reseed (drops existing data)
```

## Security Considerations

- Never commit `.env` or `.env.production` files
- Use strong JWT secrets (64+ characters)
- Configure CORS to only allow trusted origins
- Keep PostgreSQL and Redis credentials secure
- Rotate secrets periodically
- Use different credentials for dev and production
- Review Trivy security scan results

## Contributing

1. Each directory (client/server) has its own dependencies and scripts
2. Use the provided npm scripts for quality checks
3. Follow the existing code structure and patterns
4. Ensure all tests pass before submitting

## License

GNU GPLv3

## Support

For issues or questions:
- Review [DOCKER.md](./DOCKER.md) for Docker setup
- Review [CICD.md](./CICD.md) for CI/CD pipeline
- Check GitHub Issues
