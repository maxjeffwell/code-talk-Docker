# CI/CD Pipeline Guide

This guide explains the Continuous Integration and Continuous Deployment (CI/CD) setup for the code-talk application using GitHub Actions.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Setting Up GitHub Secrets](#setting-up-github-secrets)
- [Docker Hub Setup](#docker-hub-setup)
- [Workflow Triggers](#workflow-triggers)
- [Understanding the Pipelines](#understanding-the-pipelines)
- [Troubleshooting](#troubleshooting)

## Overview

The code-talk project uses GitHub Actions for automated testing, building, and deploying Docker images. Each repository (server and client) has its own independent CI/CD pipeline.

### Architecture

```
GitHub Push/PR
      │
      ├─── Server Repo ────┐
      │                    │
      │    ┌──────────────▼────────────┐
      │    │  CI Workflow              │
      │    │  - Test on Node 18 & 20   │
      │    │  - Build Docker image     │
      │    │  - Test container         │
      │    └───────────────────────────┘
      │
      │    ┌──────────────▼────────────┐
      │    │  Docker Build & Push      │
      │    │  - Build multi-platform   │
      │    │  - Push to Docker Hub     │
      │    │  - Security scan (Trivy)  │
      │    └──────────┬────────────────┘
      │               │
      │               ▼
      │         Docker Hub
      │         maxjeffwell/
      │         code-talk-graphql-server
      │
      └─── Client Repo ────┐
                           │
           ┌───────────────▼───────────┐
           │  CI Workflow              │
           │  - Test on Node 18 & 20   │
           │  - Lint & Build           │
           │  - Build Docker image     │
           │  - Test container         │
           └───────────────────────────┘

           ┌───────────────▼───────────┐
           │  Docker Build & Push      │
           │  - Build multi-platform   │
           │  - Push to Docker Hub     │
           │  - Security scan (Trivy)  │
           └──────────┬────────────────┘
                      │
                      ▼
                Docker Hub
                maxjeffwell/
                code-talk-graphql-client
```

## GitHub Actions Workflows

### Server Workflows

Located in `code-talk-graphql-server/.github/workflows/`

#### 1. CI Workflow (`ci.yml`)
**Purpose**: Continuous Integration - Test code quality and Docker builds

**Triggers**:
- Push to `main`, `master`, or `develop` branches
- Pull requests to these branches

**Jobs**:
- **Test Matrix**: Runs on Node.js 18.x and 20.x
- **Install Dependencies**: `npm ci`
- **Run Tests**: `npm test`
- **Build Docker Image**: Tests production Dockerfile build
- **Test Container**: Starts container and verifies it runs

#### 2. Docker Build & Push (`docker-build-push.yml`)
**Purpose**: Build and publish Docker images

**Triggers**:
- Push to `main` or `master` branches
- Git tags matching `v*` (e.g., v1.0.0)
- Manual workflow dispatch

**Jobs**:
- **Multi-platform Build**: Builds for `linux/amd64` and `linux/arm64`
- **Push to Docker Hub**: Publishes to `maxjeffwell/code-talk-graphql-server`
- **Security Scan**: Runs Trivy vulnerability scanner
- **Upload Results**: Sends scan results to GitHub Security tab

### Client Workflows

Located in `code-talk-graphql-client/.github/workflows/`

#### 1. CI Workflow (`ci.yml`)
**Purpose**: Continuous Integration - Test code quality and Docker builds

**Triggers**:
- Push to `main`, `master`, or `develop` branches
- Pull requests to these branches

**Jobs**:
- **Test Matrix**: Runs on Node.js 18.x and 20.x
- **Install Dependencies**: `npm ci`
- **Run Linting**: ESLint checks (warnings allowed)
- **Run Tests**: Jest tests with `--passWithNoTests`
- **Build React App**: Production build with `CI=false`
- **Build Docker Image**: Tests production Dockerfile build
- **Test Container**: Starts container on port 5001

#### 2. Docker Build & Push (`docker-build-push.yml`)
**Purpose**: Build and publish Docker images

**Triggers**:
- Push to `main` or `master` branches
- Git tags matching `v*`
- Manual workflow dispatch

**Jobs**:
- **Multi-platform Build**: Builds for `linux/amd64` and `linux/arm64`
- **Push to Docker Hub**: Publishes to `maxjeffwell/code-talk-graphql-client`
- **Security Scan**: Runs Trivy vulnerability scanner
- **Upload Results**: Sends scan results to GitHub Security tab

## Setting Up GitHub Secrets

Both repositories need the following secrets configured.

### Step 1: Get Docker Hub Credentials

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Name it: `github-actions-code-talk`
5. Copy the generated token (you won't see it again!)

### Step 2: Add Secrets to Server Repository

1. Go to https://github.com/maxjeffwell/code-talk-graphql-server
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DOCKERHUB_USERNAME` | `maxjeffwell` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | `<your_token>` | Docker Hub access token |

### Step 3: Add Secrets to Client Repository

1. Go to https://github.com/maxjeffwell/code-talk-graphql-client
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DOCKERHUB_USERNAME` | `maxjeffwell` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | `<your_token>` | Docker Hub access token |

### Step 4: Verify Secrets

```bash
# Push a test commit to trigger workflows
cd code-talk-graphql-server
git commit --allow-empty -m "Test CI/CD pipeline"
git push origin master

cd ../code-talk-graphql-client
git commit --allow-empty -m "Test CI/CD pipeline"
git push origin master
```

Check workflow status:
- Server: https://github.com/maxjeffwell/code-talk-graphql-server/actions
- Client: https://github.com/maxjeffwell/code-talk-graphql-client/actions

## Docker Hub Setup

### Create Docker Hub Repositories

If they don't exist yet:

1. Go to https://hub.docker.com/
2. Click **Create Repository**
3. Create two repositories:
   - **Name**: `code-talk-graphql-server`
     - Visibility: Public (or Private)
     - Description: "Apollo GraphQL server for code-talk application"

   - **Name**: `code-talk-graphql-client`
     - Visibility: Public (or Private)
     - Description: "React client for code-talk application"

### Verify Repositories

After first workflow run, verify images at:
- https://hub.docker.com/r/maxjeffwell/code-talk-graphql-server
- https://hub.docker.com/r/maxjeffwell/code-talk-graphql-client

## Workflow Triggers

### Automatic Triggers

#### CI Workflow
Runs on every:
- Push to `main`, `master`, or `develop` branches
- Pull request to these branches

Example:
```bash
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
# Create PR → CI runs automatically
```

#### Docker Build & Push
Runs on:
- Push to `main` or `master` (production branches)
- Git tags starting with `v` (releases)

Example:
```bash
# Merge to main triggers build
git checkout main
git merge feature/new-feature
git push origin main
# → Docker image built and pushed

# Create release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# → Docker image built with version tags
```

### Manual Triggers

You can manually trigger the Docker Build & Push workflow:

1. Go to GitHub Actions tab
2. Select **Docker Build and Push** workflow
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

Or via GitHub CLI:
```bash
gh workflow run docker-build-push.yml
```

## Understanding the Pipelines

### Image Tagging Strategy

Docker images are tagged with multiple tags:

| Tag Type | Example | When Applied |
|----------|---------|--------------|
| `latest` | `latest` | Every push to main/master |
| Branch | `main`, `develop` | Push to that branch |
| Semantic Version | `1.0.0`, `1.0` | Git tags like `v1.0.0` |
| Commit SHA | `main-abc1234` | Every build |

Example tags for server:
```
maxjeffwell/code-talk-graphql-server:latest
maxjeffwell/code-talk-graphql-server:main
maxjeffwell/code-talk-graphql-server:1.0.0
maxjeffwell/code-talk-graphql-server:1.0
maxjeffwell/code-talk-graphql-server:main-abc1234
```

### Multi-Platform Builds

Images are built for both:
- **linux/amd64**: Intel/AMD processors (most servers)
- **linux/arm64**: ARM processors (Apple Silicon, AWS Graviton, Raspberry Pi)

This means you can run the same image on:
- Ubuntu servers
- macOS M1/M2/M3
- AWS Graviton instances
- Kubernetes clusters with mixed architectures

### Security Scanning

Every build is scanned with **Trivy** for:
- Vulnerabilities in base images
- Vulnerabilities in npm packages
- Misconfigurations
- Exposed secrets

Results are:
- Displayed in workflow logs
- Uploaded to GitHub Security tab (Code scanning alerts)
- Continues even if vulnerabilities found (`continue-on-error: true`)

### Build Caching

To speed up builds, the workflows use:
- **npm cache**: Caches `node_modules` between runs
- **Docker layer cache**: Reuses unchanged layers
- **Registry cache**: Stores cache in Docker Hub

This reduces build times from ~10 minutes to ~2-3 minutes.

## Troubleshooting

### CI Workflow Failures

#### "npm ci failed"
**Problem**: Dependency installation error

**Solution**:
```bash
# Test locally
npm ci

# If lockfile is out of sync
npm install
git add package-lock.json
git commit -m "Update package-lock.json"
git push
```

#### "Docker build failed"
**Problem**: Dockerfile syntax or build error

**Solution**:
```bash
# Test build locally
docker build -t test-build .

# Check Dockerfile syntax
# Fix issues and push
git add Dockerfile
git commit -m "Fix Dockerfile"
git push
```

#### "Test container failed to start"
**Problem**: Container crashes immediately

**Solution**:
```bash
# Check logs in GitHub Actions
# View "Test Docker image" step

# Test locally
docker run --rm test-image
docker logs <container-id>
```

### Docker Build & Push Failures

#### "Login to Docker Hub failed"
**Problem**: Invalid credentials

**Solution**:
1. Verify secrets in GitHub Settings → Secrets
2. Regenerate Docker Hub token
3. Update `DOCKER_PASSWORD` secret
4. Re-run workflow

#### "Permission denied - push to Docker Hub"
**Problem**: Insufficient permissions

**Solution**:
1. Verify Docker Hub repository exists
2. Check repository is not private (unless using Pro account)
3. Verify access token has "Read, Write, Delete" permissions

#### "Trivy scanner timeout"
**Problem**: Security scan takes too long

**Solution**:
- This is non-critical (`continue-on-error: true`)
- Workflow continues even if scan fails
- Check Trivy logs for issues
- May need to increase timeout in workflow

#### "Multi-platform build failed"
**Problem**: ARM build fails

**Solution**:
```yaml
# Temporarily disable ARM builds
env:
  DOCKER_PLATFORMS: linux/amd64
```

### Viewing Workflow Logs

```bash
# Install GitHub CLI
brew install gh  # macOS
# or sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# List workflow runs
gh run list --repo maxjeffwell/code-talk-graphql-server

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Manually Triggering Workflows

```bash
# Trigger Docker build
gh workflow run docker-build-push.yml --repo maxjeffwell/code-talk-graphql-server

# Trigger with specific branch
gh workflow run docker-build-push.yml --ref develop

# Check status
gh run watch
```

### Re-running Failed Workflows

In GitHub UI:
1. Go to Actions tab
2. Click on failed workflow run
3. Click **Re-run all jobs** or **Re-run failed jobs**

Via CLI:
```bash
gh run rerun <run-id>
```

## Workflow Status Badges

Add badges to your README to show workflow status:

### Server
```markdown
[![CI](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/ci.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/ci.yml)
[![Docker](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-server/actions/workflows/docker-build-push.yml)
```

### Client
```markdown
[![CI](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/ci.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/ci.yml)
[![Docker](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/maxjeffwell/code-talk-graphql-client/actions/workflows/docker-build-push.yml)
```

## Best Practices

### Version Tagging

When releasing a new version:

```bash
# Update version in package.json
npm version patch  # 1.0.0 → 1.0.1
# or
npm version minor  # 1.0.0 → 1.1.0
# or
npm version major  # 1.0.0 → 2.0.0

# This creates a git tag
git push origin master --tags

# Workflow builds and tags images:
# - maxjeffwell/code-talk-graphql-server:1.0.1
# - maxjeffwell/code-talk-graphql-server:1.0
# - maxjeffwell/code-talk-graphql-server:latest
```

### Using Specific Versions

In docker-compose.prod.yml:
```yaml
services:
  server:
    image: maxjeffwell/code-talk-graphql-server:1.0.1  # Specific version
    # or
    image: maxjeffwell/code-talk-graphql-server:1.0    # Minor version
    # or
    image: maxjeffwell/code-talk-graphql-server:latest # Latest build
```

### Security

1. **Never commit secrets** to git
2. **Use GitHub Secrets** for credentials
3. **Rotate tokens** periodically (every 90 days)
4. **Review Trivy scans** regularly
5. **Update base images** to patch vulnerabilities

### Monitoring

1. **Enable notifications**: GitHub Settings → Notifications
2. **Watch repositories**: Get notified on workflow failures
3. **Check Docker Hub**: Monitor image pulls and sizes
4. **Review Security tab**: Check vulnerability reports

## Next Steps

1. ✅ Set up GitHub secrets (DOCKER_USERNAME, DOCKER_PASSWORD)
2. ✅ Push code to trigger workflows
3. ✅ Verify images on Docker Hub
4. ✅ Add workflow badges to README
5. 🔄 Deploy to Kubernetes (see KUBERNETES.md)
6. 🔄 Set up monitoring and alerts

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)
- [Docker Hub](https://hub.docker.com/)

## Support

For CI/CD issues:
1. Check workflow logs in GitHub Actions tab
2. Review this troubleshooting guide
3. Test Docker builds locally
4. Open an issue on GitHub
