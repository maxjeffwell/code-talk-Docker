# AGENTS.md

This document provides comprehensive guidance for AI agents working with the Code Talk project, a real-time collaborative coding platform.

---

## Project Overview

**Code Talk** is a production-ready, real-time collaborative coding platform that enables developers to work together through a modern web-based interface. Built as a full-stack application with GraphQL API and React frontend, it showcases enterprise-grade development practices including containerization, CI/CD automation, and real-time communication.

### Purpose

**Primary Goal**: Enable developers to collaborate on code in real-time through a web-based platform with instant synchronization and messaging capabilities.

**Secondary Goals**:
- Provide real-time messaging and chat functionality for team communication
- Support collaborative text editing with live synchronization across multiple users
- Demonstrate modern full-stack development practices and architectural patterns
- Showcase GraphQL subscriptions for implementing real-time features at scale

### Target Audience

**Primary Users**: Software developers and engineering teams requiring real-time collaboration tools.

**Use Cases**:
- Pair programming sessions with distributed teams
- Code review discussions with live feedback
- Technical team chat and collaboration
- Real-time coding tutorials and demonstrations
- Remote mentoring and training sessions

### Business Domain

**Domain**: Developer Tools and Collaboration

The platform addresses the growing need for remote collaboration in software development, providing tools that enable seamless real-time interaction between developers regardless of their physical location.

### License

GNU General Public License v3.0 (GPLv3)

---

## Architecture

### Architectural Pattern

**Monorepo Structure**: Contains two independent applications (client and server) in a single repository, enabling simplified development while maintaining service independence.

**Microservices-Ready**: Containerized architecture designed for horizontal scaling and orchestration with Kubernetes.

### Communication Architecture

**GraphQL API**: Single endpoint for all data operations using GraphQL over HTTP for queries/mutations and WebSocket for subscriptions.

**Real-time Layer**: Redis pub/sub enables message distribution across multiple server instances, supporting horizontal scaling while maintaining real-time synchronization.

### Data Architecture

**Primary Database**: PostgreSQL 16 with Sequelize ORM for relational data persistence (users, messages, rooms).

**Caching Layer**: Redis 7 for session management, subscription coordination, and high-speed data caching.

**Authentication**: JWT-based stateless authentication enabling horizontal scaling without shared session storage.

### Key Features

1. **Authentication & Authorization**
   - User registration and login with secure password hashing
   - JWT token-based session management
   - Protected GraphQL resolvers with role-based access control
   - bcrypt password hashing (never stores plain text)

2. **Real-time Messaging**
   - Live chat with instant message delivery to all connected users
   - GraphQL subscriptions over WebSocket for push notifications
   - Redis pub/sub for broadcasting messages across server instances
   - Message history with cursor-based pagination

3. **Collaborative Text Editing**
   - Multiple users can edit text simultaneously
   - Live synchronization using GraphQL subscriptions
   - Debounced input reduces network traffic
   - Conflict-free updates through server coordination

4. **Room Management**
   - Create and join collaborative coding/chat rooms
   - User-room associations with access control
   - PostgreSQL models for persistent room data

5. **Optimized Data Fetching**
   - DataLoader pattern for batch loading
   - Request-level caching prevents duplicate queries
   - N+1 query problem resolution
   - Cursor-based pagination for scalable data loading

6. **Modern Responsive UI**
   - Mobile-friendly interface with custom styling
   - styled-components with centralized theme system
   - Custom web fonts for professional appearance
   - Responsive design patterns for all screen sizes

---

## Technology Stack

### Languages & Runtimes

**JavaScript (ES6+)**
- Modern JavaScript features: async/await, arrow functions, destructuring, template literals
- **Server Runtime**: Node.js 20.x
- **Client Runtime**: Node.js 18.x
- **Transpiler**: Babel 7.28.0 with preset-env for compatibility

### Backend Technologies

**Core Frameworks**:
- **Apollo Server 3.13.0**: Production-ready GraphQL server implementation with built-in caching and tooling
- **Express.js 4.21.1**: Minimal and flexible web application framework
- **Sequelize 6.37.7**: Promise-based PostgreSQL ORM with migrations and associations

**GraphQL Stack**:
- **GraphQL 16.11.0**: Query language and runtime
- **graphql-ws 5.14.2**: WebSocket server for GraphQL subscriptions
- **graphql-redis-subscriptions 2.7.0**: Redis-backed pub/sub engine for scalable subscriptions
- **DataLoader 2.2.3**: Batching and caching layer for efficient data loading
- **graphql-depth-limit 1.1.0**: Prevents complex queries that could impact performance
- **graphql-query-complexity 1.1.0**: Limits query complexity to prevent resource exhaustion

**Authentication & Security**:
- **jsonwebtoken 9.0.2**: JWT token generation and verification for stateless authentication
- **bcryptjs 3.0.2**: Password hashing with configurable salt rounds
- **helmet 8.1.0**: Security headers middleware (XSS, CSP, HSTS, etc.)
- **cors 2.8.5**: Cross-Origin Resource Sharing configuration
- **express-rate-limit 7.5.1**: Rate limiting middleware for API protection
- **dompurify 3.2.6**: XSS sanitization for user-generated content

**Database & Caching**:
- **PostgreSQL 16**: Primary relational database with ACID compliance
- **Redis 7**: In-memory data store for caching and pub/sub
- **ioredis 5.6.1**: High-performance Redis client with cluster support
- **pg 8.16.3**: PostgreSQL client for Node.js

**Logging & Monitoring**:
- **winston 3.17.0**: Flexible logging library with multiple transports
- **winston-daily-rotate-file 5.0.0**: Automatic log rotation to prevent disk issues
- **morgan 1.10.0**: HTTP request logger middleware

### Frontend Technologies

**Core Libraries**:
- **React 18.3.1**: Component-based UI library with hooks and concurrent features
- **React DOM 18.3.1**: React renderer for web browsers
- **React Router 6.30.1**: Declarative routing with nested routes and code splitting

**GraphQL Client**:
- **Apollo Client 3.13.8**: Comprehensive GraphQL client with intelligent caching
- **graphql-ws 6.0.5**: WebSocket client for GraphQL subscriptions
- **@apollo/client**: Integrated data fetching, caching, and state management

**Styling & UI**:
- **styled-components 5.3.11**: CSS-in-JS with theme support and dynamic styling
- **webfontloader 1.6.28**: Asynchronous custom font loading
- **react-textarea-autosize 8.5.3**: Auto-expanding textarea component

**Utilities**:
- **lodash 4.17.21**: Utility library for data manipulation
- **prop-types 15.8.1**: Runtime type checking for React props
- **react-helmet-async 2.0.5**: Document head management for SEO
- **react-window 1.8.11**: Virtualized list rendering for performance

### Development Tools

**Build Tools**:
- **react-scripts 5.0.1**: Create React App build configuration and scripts
- **Babel**: ES6+ transpilation with preset-env
- **nodemon 3.1.10**: Development server with automatic restart on file changes

**Code Quality**:
- **ESLint**: JavaScript linting with Airbnb style guide
  - Server: eslint-config-airbnb-base
  - Client: eslint-config-airbnb with React plugins
- **Prettier 3.3.3**: Automatic code formatting for consistency
- **graphql-schema-linter**: GraphQL schema validation and best practices

### Testing Frameworks

**Server Testing**:
- **Mocha 11.7.1**: Feature-rich JavaScript test framework
- **Chai 4.3.0**: BDD/TDD assertion library
- **axios 1.7.9**: HTTP client for API testing

**Client Testing**:
- **Jest**: Testing framework with built-in mocking and assertions
- **@testing-library/react 14.0.0**: React component testing utilities
- **@testing-library/jest-dom 6.1.5**: Custom Jest matchers for DOM
- **@testing-library/user-event 14.5.1**: User interaction simulation

### Containerization & Orchestration

**Docker Stack**:
- **Docker**: Container platform for consistent environments
- **Docker Compose**: Multi-container application orchestration
- **Multi-stage Builds**: Optimized production images
- **Nginx**: Reverse proxy and load balancer for routing

**Kubernetes** (Planned):
- Container orchestration platform
- Auto-scaling and load balancing
- Self-healing deployments
- Manifests available in `k8s/` directory

### CI/CD Pipeline

**GitHub Actions**:
- **CI Workflow**: Automated testing, linting, and build verification
  - Matrix testing on Node.js 18.x and 20.x
  - ESLint and Prettier checks
  - Docker image build verification
- **Docker Build & Push Workflow**: Multi-platform image builds
  - Builds for linux/amd64 and linux/arm64
  - Automatic tagging (latest, version, branch, SHA)
  - Push to Docker Hub registry

**Security Scanning**:
- **Trivy**: Vulnerability scanner for containers and dependencies
  - Scans Docker images for known vulnerabilities
  - Uploads results to GitHub Security tab
  - Runs on every build

### Deployment Platforms

**Current Production**:
- **Heroku**: Current production deployment platform
  - Server: https://code-talk-server-5f982138903e.herokuapp.com
  - Client: https://code-talk-client-c46118c24c30.herokuapp.com
  - Separate deployments using buildpacks
  - Managed PostgreSQL and Redis add-ons

**Container Registry**:
- **Docker Hub**: Public container image repository
  - maxjeffwell/code-talk-graphql-server
  - maxjeffwell/code-talk-graphql-client
  - Automated builds via GitHub Actions
  - Multi-platform support (amd64, arm64)

**Future Deployment**:
- **Kubernetes**: Planned migration for better scalability
  - Auto-scaling based on load
  - Self-healing deployments
  - Advanced routing and load balancing
  - Resource optimization

---

## Coding Standards

### Syntax Rules

#### ES6+ Modern JavaScript (Required)

Use modern JavaScript features throughout the codebase:
- **async/await** for asynchronous operations (preferred over callbacks and raw promises)
- **Arrow functions** for concise function syntax
- **Destructuring** for cleaner object and array access
- **Template literals** for string interpolation
- **Spread/rest operators** for array and object manipulation
- **Optional chaining** (?.) for safe property access
- **Nullish coalescing** (??) for default values

#### Babel Transpilation (Required)

All ES6+ code is transpiled using Babel preset-env to ensure compatibility with target environments. The build process automatically handles this.

### Style Guidelines

#### ESLint with Airbnb Configuration (Required)

Follow the Airbnb JavaScript Style Guide for consistent code formatting:
- **Server**: Uses `eslint-config-airbnb-base` for Node.js code
- **Client**: Uses `eslint-config-airbnb` with React-specific rules

Key rules:
- 2-space indentation
- Single quotes for strings
- Semicolons required
- Trailing commas in multi-line structures
- No unused variables

#### Prettier Integration (Required)

Automatic code formatting is enforced via Prettier:
- Configured to work alongside ESLint
- Automatic formatting on save (recommended)
- Consistent code style across the entire codebase
- Run `npm run lint` to check for issues

#### React Component Structure (Recommended)

Separate concerns in React components:
- **Container Components**: Handle data fetching, state management, and business logic
- **Presentational Components**: Focus purely on UI rendering and user interaction
- Keep components focused on a single responsibility
- Use functional components with hooks (class components deprecated)

#### Styled Components (Required)

All styling must use styled-components:
- Component-scoped CSS prevents style conflicts
- Theme integration for consistent design tokens
- Dynamic styling based on props
- No external CSS files or inline styles

### Naming Conventions

#### React Component Files (Required)

- Component files must match the component name
- Use PascalCase for component names (e.g., `MessageList.js`, `UserProfile.js`)
- Index files should re-export the main component
- Place components in dedicated directories

#### GraphQL Schema Linting (Required)

- Enum values must be sorted alphabetically
- Use consistent naming for types, queries, mutations, and subscriptions
- Enforced by `graphql-schema-linter`

#### Descriptive Variable Names (Recommended)

- Use clear, descriptive names that convey intent
- Avoid abbreviations unless widely understood
- Boolean variables should start with `is`, `has`, `should`, etc.
- Functions should use verb prefixes (get, set, create, delete, etc.)

### Architecture Patterns

#### Schema Organization (Required)

GraphQL schemas must be organized by domain:
- Separate files for each domain: `user.js`, `message.js`, `editor.js`
- Link schema for base types and scalars
- Schema composition in main index file
- Clear separation of concerns

#### Resolver Organization (Required)

Group resolvers by domain with separation of concerns:
- Domain resolvers: `user.js`, `message.js`, `editor.js`
- Cross-cutting concerns: `authorization.js` for auth checks
- Combine resolvers in main index file
- Keep resolvers focused and testable

#### DataLoader Pattern (Required)

Use DataLoader for all relational data fetching:
- Prevents N+1 query problems
- Batch loading of related entities
- Request-level caching
- Create DataLoaders in context initialization

#### Higher-Order Components (Recommended)

Use HOCs for cross-cutting concerns:
- `withSession`: Inject session data into components
- `withAuthorization`: Protect routes requiring authentication
- Keep HOCs focused on a single concern
- Document props added by HOCs

### Security Requirements

#### JWT Token Management (Required)

- Use JWT for stateless authentication
- **Secret keys must be 64+ characters** in production
- Store tokens securely (localStorage for web, secure storage for mobile)
- Include expiration times on all tokens
- Validate tokens on every protected request

#### Password Hashing (Required)

- Hash all passwords using bcrypt before storage
- **Never store plain text passwords**
- Use appropriate salt rounds (10+ for production)
- Verify passwords using bcrypt compare function

#### CORS Configuration (Required)

- Configure CORS to allow only trusted origins
- Never use `*` wildcard in production
- Specify allowed methods and headers explicitly
- Set appropriate credentials policy

#### Input Sanitization (Required)

- Sanitize all user input to prevent XSS attacks
- Use DOMPurify for HTML content
- Validate input types and formats
- Implement GraphQL input validation

#### Environment Variables (Required)

- **Never commit `.env` files or secrets to git**
- Use environment variables for all sensitive data
- Different credentials for development and production
- Rotate secrets periodically
- Document required environment variables

#### Security Headers (Required)

- Use Helmet.js for secure HTTP headers
- Configure CSP (Content Security Policy)
- Enable HSTS for HTTPS enforcement
- Set appropriate X-Frame-Options

### Performance Guidelines

#### Cursor-based Pagination (Required)

- Use cursor-based pagination for all list queries
- More scalable than offset-based pagination
- Supports infinite scrolling
- Includes hasNextPage information

#### Request-level Caching (Required)

- Implement DataLoader caching to prevent duplicate queries
- Cache duration should match request lifecycle
- Clear cache between requests
- Use Redis for cross-request caching when appropriate

#### GraphQL Query Complexity (Required)

- Limit query depth to prevent deeply nested queries
- Set complexity limits based on cost analysis
- Reject queries exceeding thresholds
- Use graphql-depth-limit and graphql-query-complexity

### Testing Standards

#### Test Coverage (Recommended)

Write tests for critical functionality:
- **Server**: Mocha + Chai for resolvers, models, and API integration
- **Client**: Jest + Testing Library for React components
- Focus on business logic and user interactions
- Aim for meaningful coverage, not just percentages

#### Test File Location (Required)

- **Server tests**: Place in `src/tests/` directory
- **Client tests**: Colocate with components or in `__tests__` directories
- Name test files: `*.spec.js` (server) or `*.test.js` (client)
- Keep test utilities in separate files

### Documentation Guidelines

#### Code Comments (Recommended)

Document complex logic and non-obvious patterns:
- Explain the "why" not the "what"
- Document business rules and constraints
- Add JSDoc comments for public APIs
- Keep comments up-to-date with code changes

#### GraphQL Schema Documentation (Recommended)

- Document types, queries, mutations, and subscriptions
- Explain parameters and return types
- Document authorization requirements
- Include usage examples for complex operations

### Git Workflow

#### Commit Messages (Recommended)

Write clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Start with a verb (Add, Update, Fix, Remove, Refactor)
- Explain why, not just what
- Reference issue numbers when applicable

#### Branch Strategy (Recommended)

- **main/master**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature branches (e.g., `feature/user-authentication`)
- **bugfix/**: Bug fix branches
- **hotfix/**: Critical production fixes

### Docker Best Practices

#### Multi-stage Builds (Required)

- Use multi-stage Dockerfiles to minimize image size
- Separate build dependencies from runtime dependencies
- Copy only necessary files to production stage
- Use specific base image versions (not `latest`)

#### Non-root User (Required)

- Run containers as non-root user for security
- Create `nodejs` user in Dockerfile
- Set appropriate file permissions
- Never run as root in production

#### Health Checks (Required)

- Implement health check endpoints (`/health`)
- Define Docker HEALTHCHECK instructions
- Return appropriate status codes
- Include dependency checks (database, Redis)

---

## Project Structure

```
code-talk/
├── CICD.md                          # CI/CD pipeline documentation
├── DOCKER.md                        # Docker deployment guide
├── KUBERNETES.md                    # Kubernetes deployment guide
├── README.md                        # Project overview and quick start
├── docker-compose.yml               # Development Docker setup
├── docker-compose.prod.yml          # Production Docker setup
├── docker-compose.override.yml      # Local overrides
│
├── nginx/                           # Nginx reverse proxy configuration
│   └── nginx.conf                   # Nginx routing rules
│
├── k8s/                            # Kubernetes manifests
│   ├── namespace.yaml              # Kubernetes namespace definition
│   ├── configmap.yaml              # Configuration data
│   ├── secrets.yaml.example        # Secret templates
│   ├── server-deployment.yaml      # Server deployment config
│   ├── server-service.yaml         # Server service definition
│   ├── client-deployment.yaml      # Client deployment config
│   ├── client-service.yaml         # Client service definition
│   ├── ingress.yaml                # Ingress routing rules
│   └── hpa.yaml                    # Horizontal Pod Autoscaler
│
├── code-talk-graphql-server/       # Backend GraphQL API
│   ├── package.json                # Server dependencies
│   ├── Dockerfile                  # Server container image
│   ├── Procfile                    # Heroku deployment config
│   ├── CLAUDE.md                   # Claude AI guidance (server)
│   ├── README.md                   # Server documentation
│   ├── seed-data.sql              # Database seed file
│   │
│   └── src/                        # Server source code
│       ├── index.js                # Server entry point
│       │
│       ├── config/                 # Configuration files
│       │   └── database.js         # Database connection config
│       │
│       ├── models/                 # Sequelize ORM models
│       │   ├── index.js            # Model initialization
│       │   ├── user.js             # User model
│       │   ├── message.js          # Message model
│       │   └── room.js             # Room model
│       │
│       ├── schema/                 # GraphQL type definitions
│       │   ├── index.js            # Schema composition
│       │   ├── user.js             # User schema
│       │   ├── message.js          # Message schema
│       │   ├── editor.js           # Editor schema
│       │   └── schema.json         # Combined schema export
│       │
│       ├── resolvers/              # GraphQL resolvers
│       │   ├── index.js            # Resolver composition
│       │   ├── user.js             # User query/mutation resolvers
│       │   ├── message.js          # Message resolvers
│       │   ├── editor.js           # Editor resolvers
│       │   └── authorization.js    # Auth middleware
│       │
│       ├── loaders/                # DataLoader implementations
│       │   ├── user.js             # User batch loader
│       │   ├── message.js          # Message batch loader
│       │   └── room.js             # Room batch loader
│       │
│       ├── subscription/           # Real-time subscriptions
│       │   ├── index.js            # Redis pub/sub setup
│       │   ├── message.js          # Message events
│       │   ├── editor.js           # Editor events
│       │   └── room.js             # Room events
│       │
│       ├── scripts/                # Utility scripts
│       │   └── seed-rooms.js       # Room seeding script
│       │
│       ├── seeders/                # Database seeders
│       │   └── index.js            # Seed data initialization
│       │
│       ├── tests/                  # API tests
│       │   ├── api.js              # Test utilities
│       │   ├── user.spec.js        # User tests
│       │   └── message.spec.js     # Message tests
│       │
│       └── utils/                  # Utility functions
│           └── validation.js       # Input validation
│
└── code-talk-graphql-client/       # Frontend React application
    ├── package.json                # Client dependencies
    ├── Dockerfile                  # Client container image
    ├── Procfile                    # Heroku deployment config
    ├── server.js                   # Express server for SPA
    ├── CLAUDE.md                   # Claude AI guidance (client)
    ├── README.md                   # Client documentation
    │
    ├── public/                     # Static assets
    │   ├── index.html              # HTML template
    │   ├── robots.txt              # SEO crawler instructions
    │   ├── sitemap.xml             # Site structure for SEO
    │   ├── site.webmanifest        # PWA manifest
    │   ├── fonts/                  # Custom web fonts
    │   └── [various icons]         # Favicon and app icons
    │
    ├── screenshots/                # Application screenshots
    │
    └── src/                        # Client source code
        ├── index.js                # Application entry point
        ├── theme.js                # Theme configuration
        ├── setupTests.js           # Test configuration
        ├── test-utils.js           # Test utilities
        │
        ├── components/             # React components
        │   ├── App/                # Main app component with routing
        │   ├── Session/            # Authentication HOCs
        │   │   ├── withSession.js  # Session injection HOC
        │   │   └── withAuthorization.js # Route protection
        │   ├── Navigation/         # Navigation components
        │   │   ├── Auth/           # Authenticated nav
        │   │   └── NonAuth/        # Public nav
        │   ├── SignIn/             # Login form
        │   ├── SignUp/             # Registration form
        │   ├── SignOut/            # Logout component
        │   ├── Message/            # Messaging components
        │   │   ├── Messages/       # Message list with subscriptions
        │   │   ├── MessageCreate/  # New message form
        │   │   └── MessageDelete/  # Message removal
        │   ├── Editor/             # Collaborative editor
        │   ├── Room/               # Room management
        │   │   ├── RoomGrid/       # Room layout
        │   │   ├── RoomList/       # Room selection
        │   │   └── RoomCreate/     # Room creation
        │   ├── Landing/            # Landing page
        │   ├── Loading/            # Loading states
        │   ├── Error/              # Error displays
        │   └── Variables/          # Style constants
        │
        ├── constants/              # Application constants
        │   ├── routes.js           # Route definitions
        │   └── history.js          # Router history
        │
        ├── hooks/                  # Custom React hooks
        │
        └── utils/                  # Utility functions
```

### Key Directories Explained

#### Server Structure

- **`src/models/`**: Sequelize models defining database schema and relationships
- **`src/schema/`**: GraphQL type definitions organized by domain
- **`src/resolvers/`**: GraphQL resolvers implementing business logic
- **`src/loaders/`**: DataLoader implementations for efficient batch loading
- **`src/subscription/`**: Real-time subscription handlers with Redis pub/sub
- **`src/tests/`**: API integration tests

#### Client Structure

- **`src/components/`**: React components organized by feature
- **`src/components/Session/`**: Authentication HOCs and session management
- **`src/components/Message/`**: Real-time messaging UI components
- **`src/components/Room/`**: Room management and navigation
- **`src/constants/`**: Route definitions and configuration
- **`src/hooks/`**: Reusable custom React hooks

#### Infrastructure

- **`nginx/`**: Reverse proxy configuration for routing requests
- **`k8s/`**: Kubernetes manifests for container orchestration
- **Root level**: Docker Compose files for local development and production

---

## External Resources

### Framework Documentation

#### React
- **URL**: https://react.dev/
- **Purpose**: Official React documentation and guides for building user interfaces
- **Key Topics**: Hooks, component lifecycle, state management, performance optimization

#### Apollo Server
- **URL**: https://www.apollographql.com/docs/apollo-server/
- **Purpose**: GraphQL server implementation guide
- **Key Topics**: Schema design, resolvers, subscriptions, caching, performance

#### Apollo Client
- **URL**: https://www.apollographql.com/docs/react/
- **Purpose**: React Apollo Client integration and usage
- **Key Topics**: Queries, mutations, subscriptions, cache management, optimistic UI

#### styled-components
- **URL**: https://styled-components.com/docs
- **Purpose**: CSS-in-JS library documentation
- **Key Topics**: Component styling, theming, dynamic styles, server-side rendering

### Database Documentation

#### PostgreSQL
- **URL**: https://www.postgresql.org/docs/
- **Purpose**: Official PostgreSQL database documentation
- **Key Topics**: SQL syntax, indexing, transactions, performance tuning

#### Sequelize
- **URL**: https://sequelize.org/docs/
- **Purpose**: PostgreSQL ORM for Node.js
- **Key Topics**: Model definition, associations, migrations, queries, transactions

#### Redis
- **URL**: https://redis.io/docs/
- **Purpose**: In-memory data structure store documentation
- **Key Topics**: Data types, pub/sub, persistence, clustering, performance

### GraphQL Resources

#### GraphQL Documentation
- **URL**: https://graphql.org/learn/
- **Purpose**: Official GraphQL learning resources
- **Key Topics**: Schema design, queries, mutations, subscriptions, best practices

#### GraphQL Best Practices
- **URL**: https://graphql.org/learn/best-practices/
- **Purpose**: Official GraphQL best practices guide
- **Key Topics**: Schema design, pagination, caching, security, performance

### Key Libraries

#### Express.js
- **URL**: https://expressjs.com/
- **Purpose**: Web application framework for Node.js
- **Use in Project**: HTTP server, middleware chain, route handling

#### React Router
- **URL**: https://reactrouter.com/
- **Purpose**: Declarative routing for React applications
- **Use in Project**: Client-side navigation, route protection, nested routes

#### DataLoader
- **URL**: https://github.com/graphql/dataloader
- **Purpose**: Batch loading and caching utility
- **Use in Project**: N+1 query prevention, efficient data fetching

#### jsonwebtoken
- **URL**: https://github.com/auth0/node-jsonwebtoken
- **Purpose**: JWT implementation for Node.js
- **Use in Project**: Stateless authentication, token generation and verification

#### bcryptjs
- **URL**: https://github.com/dcodeIO/bcrypt.js
- **Purpose**: Password hashing library
- **Use in Project**: Secure password storage, authentication

#### ioredis
- **URL**: https://github.com/luin/ioredis
- **Purpose**: Redis client for Node.js
- **Use in Project**: Caching, pub/sub for real-time features

### Development Tools

#### Docker
- **URL**: https://docs.docker.com/
- **Purpose**: Container platform documentation
- **Key Topics**: Dockerfile syntax, multi-stage builds, networking, volumes

#### Docker Compose
- **URL**: https://docs.docker.com/compose/
- **Purpose**: Multi-container application orchestration
- **Key Topics**: Service definition, networking, volumes, environment variables

#### Kubernetes
- **URL**: https://kubernetes.io/docs/
- **Purpose**: Container orchestration platform
- **Key Topics**: Deployments, services, ingress, scaling, self-healing

#### GitHub Actions
- **URL**: https://docs.github.com/en/actions
- **Purpose**: CI/CD automation platform
- **Key Topics**: Workflows, jobs, steps, secrets, matrix builds

#### Trivy
- **URL**: https://github.com/aquasecurity/trivy
- **Purpose**: Security vulnerability scanner
- **Key Topics**: Container scanning, dependency scanning, policy enforcement

#### ESLint
- **URL**: https://eslint.org/docs/
- **Purpose**: JavaScript linting utility
- **Key Topics**: Rules, plugins, configuration, custom rules

#### Prettier
- **URL**: https://prettier.io/docs/
- **Purpose**: Code formatting tool
- **Key Topics**: Configuration, editor integration, pre-commit hooks

### Deployment Platforms

#### Heroku
- **URL**: https://devcenter.heroku.com/
- **Purpose**: Cloud platform for application deployment (current production)
- **Production URLs**:
  - Server: https://code-talk-server-5f982138903e.herokuapp.com
  - Client: https://code-talk-client-c46118c24c30.herokuapp.com

#### Docker Hub
- **URL**: https://hub.docker.com/
- **Purpose**: Container image registry
- **Project Repositories**:
  - maxjeffwell/code-talk-graphql-server
  - maxjeffwell/code-talk-graphql-client

#### GitHub
- **URL**: https://github.com/
- **Purpose**: Version control and CI/CD platform
- **Use in Project**: Source control, automated builds, security scanning

### Best Practices Guides

#### React Best Practices
- **URL**: https://react.dev/learn/thinking-in-react
- **Topics**: Component design, state management, performance, testing

#### Node.js Best Practices
- **URL**: https://github.com/goldbergyoni/nodebestpractices
- **Topics**: Project structure, error handling, security, testing, performance

#### Docker Best Practices
- **URL**: https://docs.docker.com/develop/dev-best-practices/
- **Topics**: Image optimization, security, networking, logging

#### Security Best Practices
- **URL**: https://cheatsheetseries.owasp.org/
- **Topics**: OWASP Top 10, authentication, authorization, input validation

### Community Resources

#### GraphQL Community
- **URL**: https://graphql.org/community/
- **Purpose**: GraphQL community resources and support

#### React Community
- **URL**: https://react.dev/community
- **Purpose**: React community resources and forums

---

## Additional Context

### Design Decisions & Rationale

#### GraphQL over REST
**Rationale**: Provides flexible data fetching, real-time subscriptions with WebSockets, strong typing through schema, and single endpoint for all operations. Better developer experience with tools like GraphQL Playground.

#### Apollo Server and Client
**Rationale**: Industry-standard GraphQL implementation with excellent tooling, built-in caching, subscription support, and extensive documentation. Production-ready with minimal configuration.

#### PostgreSQL
**Rationale**: Robust relational database with excellent support for complex relationships, ACID compliance, powerful query optimizer, and extensive JSON support for hybrid workloads.

#### Redis for Pub/Sub
**Rationale**: Fast, reliable message distribution for real-time features. Enables horizontal scaling by coordinating subscriptions across multiple server instances. Also provides high-speed caching.

#### JWT Authentication
**Rationale**: Stateless authentication enables horizontal scaling without shared session storage. Tokens can be validated independently by each server instance. Standard, widely supported format.

#### Monorepo Structure
**Rationale**: Simplifies development and deployment while keeping client and server services independent. Shared configuration, easier refactoring, single version control.

#### Docker Containerization
**Rationale**: Ensures consistent environments across development, testing, and production. Enables Kubernetes compatibility, simplifies deployment, and improves resource utilization.

#### styled-components
**Rationale**: Component-scoped CSS prevents style conflicts, enables dynamic styling based on props, theme integration for consistent design, better maintainability than separate CSS files.

### Development Workflow

#### Local Development

**Method**: Docker Compose orchestrates the complete stack

**Command**: `docker-compose up -d`

**Services Started**:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- GraphQL server (port 8000)
- React client (port 5000)
- Nginx reverse proxy (port 80)

**Benefits**:
- Consistent environment across team members
- Minimal local setup required
- Easy to reset and rebuild
- Mirrors production architecture

#### CI/CD Pipeline

**Platform**: GitHub Actions with two separate repositories

**Server CI Pipeline** (`code-talk-graphql-server`):
- Triggers on push to main/master/develop and pull requests
- Tests on Node.js 18.x and 20.x in parallel
- Runs `npm ci`, `npm test`, Docker build, and container test
- Status badge visible in README

**Client CI Pipeline** (`code-talk-graphql-client`):
- Triggers on push to main/master/develop and pull requests
- Tests on Node.js 18.x and 20.x in parallel
- Runs `npm ci`, ESLint, Jest tests, React build, Docker build
- Status badge visible in README

**Docker Build & Push Pipelines**:
- Triggers on push to main/master, git tags (v*), or manual dispatch
- Builds for linux/amd64 and linux/arm64 platforms
- Pushes to Docker Hub with multiple tags (latest, version, branch, SHA)
- Runs Trivy security scan and uploads results
- Continues even if security scan finds vulnerabilities

**Security Scanning**:
- Trivy scans every Docker image for vulnerabilities
- Results uploaded to GitHub Security tab
- Scans both base images and npm dependencies
- Non-blocking to allow deployment decisions

### Testing Strategy

**Server Testing**: Mocha + Chai for API integration tests
- Test GraphQL queries, mutations, and subscriptions
- Verify authentication and authorization
- Test database operations and data integrity
- Located in `src/tests/` directory

**Client Testing**: Jest + Testing Library for React component tests
- Test component rendering and user interactions
- Mock Apollo Client for GraphQL operations
- Test hooks and state management
- Colocated with components or in `__tests__` directories

**Integration Testing**: Manual testing with GraphQL Playground
- Explore schema and test queries interactively
- Test real-time subscriptions
- Verify authentication flows
- Available at http://localhost:8000/graphql

### Security Considerations

**Critical Security Measures**:
1. JWT secret must be 64+ characters for production
2. Strong PostgreSQL passwords (16+ characters minimum)
3. Strong Redis passwords (16+ characters minimum)
4. CORS configured to allow only trusted origins
5. Helmet.js for comprehensive security headers
6. Rate limiting on all API endpoints
7. bcrypt password hashing with appropriate salt rounds
8. Input sanitization with DOMPurify
9. GraphQL query depth and complexity limits
10. Trivy security scanning in CI/CD pipeline
11. Never commit .env files or secrets to git
12. Regular rotation of JWT secrets and credentials

**Vulnerability Management**:
- Automated scanning with Trivy on every build
- GitHub Security tab integration for tracking
- Regular dependency updates via npm-check-updates
- Manual security audits before major releases

### Performance Optimizations

**Data Loading**:
- DataLoader for batch loading and N+1 query prevention
- Request-level caching reduces duplicate queries
- Cursor-based pagination for scalable message history

**Caching Strategy**:
- Redis for frequently accessed data
- Apollo Client cache for client-side data
- DataLoader request-level cache
- HTTP caching headers where appropriate

**Query Optimization**:
- GraphQL query complexity limiting prevents resource exhaustion
- Query depth limiting prevents deeply nested queries
- Indexing on frequently queried database fields
- Efficient Sequelize queries with proper associations

**Build Optimization**:
- Multi-stage Docker builds minimize image sizes
- Docker layer caching speeds up CI/CD
- Production builds with minification and tree-shaking
- Code splitting in React for smaller bundles

**Real-time Optimization**:
- Debounced editor input reduces network traffic
- WebSocket connection pooling
- Redis pub/sub scales subscriptions horizontally

### Scalability Architecture

**Horizontal Scaling**:
- Stateless architecture enables multiple server instances
- JWT authentication requires no shared session storage
- Redis pub/sub coordinates subscriptions across instances
- Load balancing via Nginx or Kubernetes ingress

**Database Scaling**:
- PostgreSQL read replicas for scaling read operations
- Connection pooling for efficient resource usage
- Proper indexing for query performance

**Caching Scaling**:
- Redis cluster for distributed caching
- Redis Sentinel for high availability
- Separate cache namespaces for different data types

**Kubernetes Support**:
- Manifests ready for Kubernetes deployment
- Horizontal Pod Autoscaler configuration
- Self-healing deployments
- Resource limits and requests defined

### Deployment Strategy

**Current Production (Heroku)**:
- Separate deployments for client and server
- Managed PostgreSQL and Redis add-ons
- Automatic deployments from git push
- Environment-based configuration

**Future Migration (Kubernetes)**:
- Better scalability with auto-scaling
- Advanced deployment strategies (rolling, blue-green)
- Superior resource utilization
- Self-healing and automatic restarts
- Cost optimization through efficient resource allocation

**Container Registry (Docker Hub)**:
- Public images available for both services
- Multi-platform support (amd64, arm64)
- Automated builds via GitHub Actions
- Version tagging for rollbacks

### Environment Variables

**Server Required Variables**:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT signing (64+ chars)
- `REDIS_HOST`: Redis server hostname
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_PASSWORD`: Redis authentication password
- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (default: 8000)
- `ALLOWED_ORIGINS`: Comma-separated CORS allowed origins

**Client Required Variables**:
- `REACT_APP_GRAPHQL_HTTP_URI`: GraphQL HTTP endpoint URL
- `REACT_APP_GRAPHQL_WS_URI`: GraphQL WebSocket endpoint URL

**Optional Variables**:
- `TEST_DATABASE_URL`: Separate database for testing
- `LOG_LEVEL`: Winston logging level (info/debug/error)

### Project Maturity & Status

**Current State**: Production-ready demonstration project

**Suitable For**:
- Portfolio and resume showcase
- Learning modern full-stack development patterns
- Starting point for real-time collaboration features
- Reference implementation of GraphQL best practices
- Example of Docker and Kubernetes deployment
- CI/CD pipeline template

**Production Readiness**:
- Comprehensive error handling and logging
- Security best practices implemented
- Automated testing in CI/CD
- Container orchestration ready
- Monitoring and health checks
- Documentation for deployment and operation

**Future Enhancements**:
- Complete Kubernetes deployment with auto-scaling
- Enhanced room management with fine-grained permissions
- Real-time user presence indicators
- File upload and sharing capabilities
- Code syntax highlighting for multiple languages
- Progressive Web App features (offline support, push notifications)
- Prometheus/Grafana monitoring and alerting
- Advanced analytics and usage tracking

---

## Testing Instructions

### Server Testing

#### Running Tests
```bash
cd code-talk-graphql-server

# Run all tests
npm test

# Run with specific test file
npm run test:execute-test

# Run server in test mode
npm run test:run-server
```

#### Test Structure
- **Location**: `src/tests/` directory
- **Framework**: Mocha with Chai assertions
- **Coverage**: User authentication, message operations, GraphQL API
- **Files**:
  - `api.js`: Test utilities and helpers
  - `user.spec.js`: User authentication tests
  - `message.spec.js`: Message functionality tests

#### Writing Tests
```javascript
// Example test structure
const { expect } = require('chai');
const { createTestUser } = require('./api');

describe('User Authentication', () => {
  it('should register a new user', async () => {
    const user = await createTestUser();
    expect(user).to.have.property('token');
    expect(user).to.have.property('username');
  });
});
```

### Client Testing

#### Running Tests
```bash
cd code-talk-graphql-client

# Run tests in watch mode
npm test

# Run tests once
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage
```

#### Test Structure
- **Location**: Colocated with components or in `__tests__` directories
- **Framework**: Jest with Testing Library
- **Coverage**: React components, hooks, user interactions
- **Utilities**: Mock Apollo Client, test utilities in `test-utils.js`

#### Writing Tests
```javascript
// Example component test
import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import UserProfile from './UserProfile';

test('renders user profile', () => {
  render(
    <MockedProvider mocks={[]} addTypename={false}>
      <UserProfile />
    </MockedProvider>
  );
  expect(screen.getByText(/profile/i)).toBeInTheDocument();
});
```

### Integration Testing

#### GraphQL Playground
Access at: http://localhost:8000/graphql (when server is running)

**Example Query**:
```graphql
query GetMessages {
  messages(limit: 10) {
    edges {
      id
      text
      createdAt
      user {
        username
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

**Example Mutation**:
```graphql
mutation CreateMessage($text: String!) {
  createMessage(text: $text) {
    id
    text
    createdAt
  }
}
```

**Example Subscription**:
```graphql
subscription OnMessageCreated {
  messageCreated {
    id
    text
    user {
      username
    }
  }
}
```

### Docker Testing

#### Test Container Builds
```bash
# Test server build
cd code-talk-graphql-server
docker build -t test-server .
docker run --rm test-server

# Test client build
cd code-talk-graphql-client
docker build -t test-client .
docker run --rm -p 5000:5000 test-client
```

#### Test Complete Stack
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Build Steps

### Prerequisites

**Required Software**:
- Node.js 18.x or 20.x
- npm 8.x or higher
- Docker 20.10+ (for containerized development)
- Docker Compose 2.0+ (for multi-container setup)
- PostgreSQL 16 (if running locally without Docker)
- Redis 7 (if running locally without Docker)

### Local Development (Without Docker)

#### Server Setup

1. **Navigate to server directory**:
   ```bash
   cd code-talk-graphql-server
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL and Redis credentials
   ```

4. **Required environment variables**:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/code_talk_db
   JWT_SECRET=your_jwt_secret_minimum_64_characters_for_production
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_redis_password
   NODE_ENV=development
   PORT=8000
   ALLOWED_ORIGINS=http://localhost:3000
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

6. **Seed database (optional)**:
   ```bash
   npm run seed
   ```

#### Client Setup

1. **Navigate to client directory**:
   ```bash
   cd code-talk-graphql-client
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   ```bash
   # Create .env file if custom endpoints needed
   REACT_APP_GRAPHQL_HTTP_URI=http://localhost:8000/graphql
   REACT_APP_GRAPHQL_WS_URI=ws://localhost:8000/graphql
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

5. **Access application**:
   - Frontend: http://localhost:3000
   - GraphQL API: http://localhost:8000/graphql

### Docker Development

#### Quick Start

1. **Navigate to project root**:
   ```bash
   cd code-talk
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Access application**:
   - Frontend: http://localhost
   - GraphQL API: http://localhost/graphql
   - Direct Server: http://localhost:8000/graphql

6. **Seed database**:
   ```bash
   docker-compose exec server npm run seed
   ```

7. **Stop services**:
   ```bash
   docker-compose down
   ```

#### Build from Source

1. **Build images locally**:
   ```bash
   docker-compose build
   ```

2. **Build specific service**:
   ```bash
   docker-compose build server
   docker-compose build client
   ```

3. **Rebuild with no cache**:
   ```bash
   docker-compose build --no-cache
   ```

### Production Build

#### Docker Production

1. **Configure production environment**:
   ```bash
   cp .env.production.example .env.production
   # Edit with production values
   ```

2. **Generate secure secrets**:
   ```bash
   # JWT secret (64 characters)
   openssl rand -base64 64

   # Database password
   openssl rand -base64 32
   ```

3. **Start production stack**:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
   ```

4. **Monitor logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

#### Server Production Build

1. **Build for production**:
   ```bash
   cd code-talk-graphql-server
   npm install --production
   ```

2. **Start server**:
   ```bash
   npm start
   ```

#### Client Production Build

1. **Build React app**:
   ```bash
   cd code-talk-graphql-client
   npm run build
   ```

2. **Serve static files**:
   ```bash
   npm start
   ```

### Database Management

#### Create Database

**PostgreSQL**:
```sql
CREATE DATABASE code_talk_db;
CREATE USER code_talk_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE code_talk_db TO code_talk_user;
```

#### Run Migrations

```bash
# Using Docker
docker-compose exec server npm run migrate

# Local
cd code-talk-graphql-server
npm run migrate
```

#### Seed Database

```bash
# Basic seed
npm run seed

# Force reseed (drops existing data)
npm run seed:force

# Seed rooms only
npm run seed:rooms
```

#### Backup Database

```bash
# Using Docker
docker-compose exec postgres pg_dump -U postgres code_talk_db > backup.sql

# With compression
docker-compose exec postgres pg_dump -U postgres code_talk_db | gzip > backup.sql.gz
```

#### Restore Database

```bash
# From SQL file
docker-compose exec -T postgres psql -U postgres code_talk_db < backup.sql

# From gzipped file
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U postgres code_talk_db
```

### CI/CD Build Process

#### GitHub Actions Workflow

**Automatic Triggers**:
- Push to main/master/develop
- Pull requests
- Git tags (v*)

**Build Process**:
1. Checkout code
2. Set up Node.js (matrix: 18.x, 20.x)
3. Install dependencies (`npm ci`)
4. Run tests
5. Build Docker image
6. Push to Docker Hub (on main/master only)
7. Run security scan with Trivy

#### Manual Trigger

```bash
# Using GitHub CLI
gh workflow run docker-build-push.yml

# Specific branch
gh workflow run docker-build-push.yml --ref develop
```

### Troubleshooting

#### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

#### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec server node -e "require('pg').Client({connectionString:process.env.DATABASE_URL}).connect().then(()=>console.log('OK'))"
```

#### Redis Connection Failed

```bash
# Check Redis is running
docker-compose exec redis redis-cli -a your_password PING

# Test from server
docker-compose exec server node -e "require('ioredis')({host:'redis',port:6379,password:process.env.REDIS_PASSWORD}).ping().then(console.log)"
```

#### Build Failures

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Docker build cache
docker builder prune -a
```

---

## Quick Reference

### Common Commands

**Development**:
```bash
# Start complete stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# Shell into server
docker-compose exec server sh

# Seed database
docker-compose exec server npm run seed
```

**Testing**:
```bash
# Server tests
cd code-talk-graphql-server && npm test

# Client tests
cd code-talk-graphql-client && npm test

# Lint code
npm run lint
```

**Database**:
```bash
# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres code_talk_db

# Access Redis CLI
docker-compose exec redis redis-cli -a your_password

# Backup database
docker-compose exec postgres pg_dump -U postgres code_talk_db > backup.sql
```

### Important URLs

**Local Development**:
- Frontend: http://localhost:3000 (or http://localhost via Nginx)
- GraphQL API: http://localhost:8000/graphql
- GraphQL Playground: http://localhost:8000/graphql

**Production**:
- Server: https://code-talk-server-5f982138903e.herokuapp.com
- Client: https://code-talk-client-c46118c24c30.herokuapp.com

**Docker Hub**:
- Server Image: https://hub.docker.com/r/maxjeffwell/code-talk-graphql-server
- Client Image: https://hub.docker.com/r/maxjeffwell/code-talk-graphql-client

---

## Support & Contributing

### Getting Help

For issues or questions:
1. Check the relevant documentation (README.md, DOCKER.md, CICD.md)
2. Review troubleshooting sections in this document
3. Check GitHub Issues for similar problems
4. Review container logs with `docker-compose logs`

### Contributing

1. Each directory (client/server) has its own dependencies and scripts
2. Use the provided npm scripts for quality checks
3. Follow the coding standards outlined in this document
4. Ensure all tests pass before submitting changes
5. Write clear, descriptive commit messages
6. Create pull requests with detailed descriptions

### Code Quality Checks

Before committing:
```bash
# Run linter
npm run lint

# Run tests
npm test

# Build to verify no errors
npm run build
```

---

**Last Updated**: 2025-12-08

**Document Version**: 1.0.0

**Maintained By**: AI Agents using Artiforge
