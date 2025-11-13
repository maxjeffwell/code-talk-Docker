# Kubernetes Deployment Guide

This guide explains how to deploy the code-talk application to Kubernetes with external PostgreSQL and Redis databases.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Database Setup](#database-setup)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring and Management](#monitoring-and-management)
- [Scaling](#scaling)
- [SSL/TLS Setup](#ssltls-setup)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

## Prerequisites

### Required Tools

```bash
# kubectl (Kubernetes CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### Required Resources

- Kubernetes cluster (Linode LKE, DigitalOcean, AWS EKS, GKE, etc.)
- `kubectl` configured to access your cluster
- Domain name pointing to your cluster
- External PostgreSQL database
- External Redis database
- Docker Hub images (already published)

## Database Setup

You need to set up **external** PostgreSQL and Redis databases before deploying. Choose one of these options:

### Option 1: Use Existing Heroku Databases (Easiest)

You already have these! Just use your existing connection strings:

```bash
# Your existing Heroku PostgreSQL


# Your existing Heroku Redis

```

**Pros:**
- ✅ Already configured
- ✅ Zero setup needed
- ✅ Can test K8s without database risk

### Option 2: Neon + Upstash (Recommended for K8s)

**Neon (PostgreSQL):**
1. Sign up at https://neon.tech
2. Create project: "code-talk"
3. Copy connection string:
   ```
   
   ```
4. Free tier: 512MB storage, unlimited compute

**Upstash (Redis):**
1. Sign up at https://upstash.com
2. Create database: "code-talk"
3. Copy connection string:
   ```
   rediss://default:pass@xxx.upstash.io:6380
   ```
4. Free tier: 10,000 commands/day

**Pros:**
- ✅ Generous free tiers
- ✅ Serverless (auto-scaling)
- ✅ Built for cloud-native apps
- ✅ Low latency

### Option 3: Managed Databases (Production)

**If using Linode LKE:**
1. Go to Linode Cloud Manager
2. Create Managed PostgreSQL ($15/mo)
3. Create your own Redis in K8s or use managed service

**If using DigitalOcean:**
1. Create Managed PostgreSQL ($15/mo)
2. Create Managed Redis ($15/mo)

**Pros:**
- ✅ Same datacenter = low latency
- ✅ Automatic backups
- ✅ Production-ready

## Quick Start

### 1. Configure Secrets

```bash
# Copy the example secrets file
cp k8s/secrets.yaml.example k8s/secrets.yaml

# Encode your database connection strings
echo -n "postgresql://user:pass@host:5432/db" | base64
echo -n "rediss://:pass@host:6380" | base64

# Generate JWT secret (64+ characters)
openssl rand -base64 64 | tr -d '\n' | base64

# Edit secrets.yaml with your base64-encoded values
vim k8s/secrets.yaml
```

### 2. Update Configuration

```bash
# Edit configmap with your domain
vim k8s/configmap.yaml

# Update ALLOWED_ORIGINS, REACT_APP_GRAPHQL_HTTP_URI, REACT_APP_GRAPHQL_WS_URI
```

### 3. Update Ingress

```bash
# Edit ingress with your domain
vim k8s/ingress.yaml

# Replace "yourdomain.com" with your actual domain
```

### 4. Deploy

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/server-deployment.yaml
kubectl apply -f k8s/server-service.yaml
kubectl apply -f k8s/client-deployment.yaml
kubectl apply -f k8s/client-service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get all -n code-talk
```

## Configuration

### Creating secrets.yaml

The `secrets.yaml.example` file contains detailed instructions. Here's a quick reference:

```bash
# 1. Copy example file
cp k8s/secrets.yaml.example k8s/secrets.yaml

# 2. Encode your values
# PostgreSQL URL
echo -n "postgresql://user:password@host:5432/database" | base64

# JWT Secret (generate new one)
openssl rand -base64 64 | tr -d '\n' | base64

# Redis URL
echo -n "rediss://:password@host:6380" | base64

# 3. Edit secrets.yaml and replace the placeholder values

# 4. NEVER commit secrets.yaml to git!
# (Already in .gitignore)
```

### Example secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: code-talk-secrets
  namespace: code-talk
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bob3N0OjU0MzIvZGI=
  JWT_SECRET: <your-base64-encoded-jwt-secret>
  REDIS_URL: cmVkaXNzOi8vOnBhc3NAaG9zdDo2Mzgw
```

### ConfigMap Values

Edit `k8s/configmap.yaml`:

```yaml
data:
  ALLOWED_ORIGINS: "https://yourdomain.com,https://www.yourdomain.com"
  REACT_APP_GRAPHQL_HTTP_URI: "https://yourdomain.com/graphql"
  REACT_APP_GRAPHQL_WS_URI: "wss://yourdomain.com/graphql"
```

### Ingress Domain

Edit `k8s/ingress.yaml`:

```yaml
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
  rules:
  - host: yourdomain.com
  - host: www.yourdomain.com
```

## Deployment

### Install Nginx Ingress Controller

If not already installed on your cluster:

```bash
# Install Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml

# Wait for LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller --watch

# Get external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

**Point your domain's A record to this IP.**

### Install cert-manager (for SSL/TLS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for pods to be ready
kubectl get pods -n cert-manager --watch

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com  # Change this!
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Deploy Application

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# 3. Create Secrets
kubectl apply -f k8s/secrets.yaml

# 4. Deploy server
kubectl apply -f k8s/server-deployment.yaml
kubectl apply -f k8s/server-service.yaml

# 5. Deploy client
kubectl apply -f k8s/client-deployment.yaml
kubectl apply -f k8s/client-service.yaml

# 6. Create Ingress
kubectl apply -f k8s/ingress.yaml

# 7. Enable autoscaling
kubectl apply -f k8s/hpa.yaml

# 8. Verify deployment
kubectl get all -n code-talk
```

### Verify Deployment

```bash
# Check pods are running
kubectl get pods -n code-talk

# Should show:
# code-talk-server-xxx   1/1   Running
# code-talk-client-xxx   1/1   Running

# Check services
kubectl get svc -n code-talk

# Check ingress
kubectl get ingress -n code-talk

# View logs
kubectl logs -n code-talk deployment/code-talk-server
kubectl logs -n code-talk deployment/code-talk-client

# Check pod health
kubectl describe pod -n code-talk <pod-name>
```

## Monitoring and Management

### View Application Logs

```bash
# Stream server logs
kubectl logs -f -n code-talk deployment/code-talk-server

# Stream client logs
kubectl logs -f -n code-talk deployment/code-talk-client

# View logs from all pods
kubectl logs -n code-talk -l app=code-talk --all-containers=true

# View logs from specific time
kubectl logs -n code-talk deployment/code-talk-server --since=1h
```

### Check Application Health

```bash
# Check pod status
kubectl get pods -n code-talk -o wide

# Check deployment status
kubectl rollout status deployment/code-talk-server -n code-talk
kubectl rollout status deployment/code-talk-client -n code-talk

# Describe resources
kubectl describe deployment code-talk-server -n code-talk
kubectl describe pod <pod-name> -n code-talk

# Check resource usage
kubectl top pods -n code-talk
kubectl top nodes
```

### Access Application

```bash
# Get ingress IP/domain
kubectl get ingress -n code-talk

# Test endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/graphql -X POST -H "Content-Type: application/json" -d '{"query":"{ __typename }"}'
```

### Update Application

```bash
# Update to new version
kubectl set image deployment/code-talk-server server=maxjeffwell/code-talk-graphql-server:v1.1.0 -n code-talk
kubectl set image deployment/code-talk-client client=maxjeffwell/code-talk-graphql-client:v1.1.0 -n code-talk

# Watch rollout
kubectl rollout status deployment/code-talk-server -n code-talk

# Rollback if needed
kubectl rollout undo deployment/code-talk-server -n code-talk

# Check rollout history
kubectl rollout history deployment/code-talk-server -n code-talk
```

## Scaling

### Manual Scaling

```bash
# Scale server deployment
kubectl scale deployment code-talk-server --replicas=5 -n code-talk

# Scale client deployment
kubectl scale deployment code-talk-client --replicas=3 -n code-talk

# Verify
kubectl get deployment -n code-talk
```

### Autoscaling (HPA)

HPA is already configured in `k8s/hpa.yaml`.

```bash
# Check HPA status
kubectl get hpa -n code-talk

# Describe HPA
kubectl describe hpa code-talk-server-hpa -n code-talk

# View autoscaling events
kubectl get events -n code-talk --field-selector involvedObject.name=code-talk-server-hpa
```

**HPA Configuration:**
- **Server**: 2-10 replicas, scales at 70% CPU or 80% memory
- **Client**: 2-5 replicas, scales at 70% CPU or 80% memory

## SSL/TLS Setup

SSL/TLS is automatically handled by cert-manager if configured.

### Verify Certificate

```bash
# Check certificate status
kubectl get certificate -n code-talk

# Describe certificate
kubectl describe certificate code-talk-tls -n code-talk

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Troubleshoot SSL Issues

```bash
# Check certificate request
kubectl get certificaterequest -n code-talk

# Check challenges
kubectl get challenges -n code-talk

# View detailed challenge info
kubectl describe challenge <challenge-name> -n code-talk
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n code-talk

# Common issues:
# - ImagePullBackOff: Check image name and Docker Hub access
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resource availability

# Check events
kubectl get events -n code-talk --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check secrets are correctly set
kubectl get secret code-talk-secrets -n code-talk -o yaml

# Decode and verify DATABASE_URL
kubectl get secret code-talk-secrets -n code-talk -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Check server logs for connection errors
kubectl logs -n code-talk deployment/code-talk-server | grep -i database

# Test connection from pod
kubectl exec -it -n code-talk deployment/code-talk-server -- /bin/sh
# Inside pod:
node -e "console.log(process.env.DATABASE_URL)"
```

### Redis Connection Issues

```bash
# Decode and verify REDIS_URL
kubectl get secret code-talk-secrets -n code-talk -o jsonpath='{.data.REDIS_URL}' | base64 -d

# Check server logs
kubectl logs -n code-talk deployment/code-talk-server | grep -i redis
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress code-talk-ingress -n code-talk

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verify DNS points to LoadBalancer IP
nslookup yourdomain.com

# Test without Ingress (port-forward)
kubectl port-forward -n code-talk svc/code-talk-client 8080:80
# Access http://localhost:8080
```

### WebSocket Issues

```bash
# Check WebSocket annotations
kubectl get ingress code-talk-ingress -n code-talk -o yaml | grep websocket

# Test WebSocket connection
wscat -c wss://yourdomain.com/graphql

# Check server logs for WebSocket errors
kubectl logs -n code-talk deployment/code-talk-server | grep -i websocket
```

## Production Checklist

### Before Deployment

- [ ] External databases set up (PostgreSQL, Redis)
- [ ] Domain DNS pointing to LoadBalancer IP
- [ ] Secrets created with strong values
- [ ] ConfigMap updated with production domain
- [ ] Ingress configured with correct domain
- [ ] cert-manager ClusterIssuer created
- [ ] Resource limits set appropriately
- [ ] HPA enabled and configured

### Security

- [ ] Use strong JWT secret (64+ characters)
- [ ] Database uses strong password
- [ ] Secrets not committed to version control
- [ ] CORS configured for production domain only
- [ ] Network policies configured (optional)
- [ ] Pod security policies enabled (optional)
- [ ] Read-only root filesystem enabled
- [ ] Non-root user enforced

### Monitoring

- [ ] Set up logging (e.g., ELK, Loki)
- [ ] Set up monitoring (e.g., Prometheus, Grafana)
- [ ] Configure alerts for pod failures
- [ ] Configure alerts for high resource usage
- [ ] Set up uptime monitoring
- [ ] Database monitoring enabled

### Backup

- [ ] Database automated backups configured (external service)
- [ ] Kubernetes manifests in version control
- [ ] Secrets backed up securely (not in git!)
- [ ] Disaster recovery plan documented

## Database Connection Examples

### Using Heroku Databases

```yaml
# k8s/secrets.yaml
data:
  DATABASE_URL: cG9zdGdyZXM6Ly91ZTJwNzE3dG1iZzd1ai4uLg==  # Your Heroku PostgreSQL
  REDIS_URL: cmVkaXNzOi8vOnA0MGUzZDQ2YjY2NTVhMi4uLg==       # Your Heroku Redis
```

### Using Neon + Upstash

```yaml
# k8s/secrets.yaml
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BlcC14eHgudXMtZWFzdC0yLmF3cy5uZW9uLnRlY2gvbmVvbmRi
  REDIS_URL: cmVkaXNzOi8vZGVmYXVsdDpwYXNzQHh4eC51cHN0YXNoLmlvOjYzODA=
```

### Using Individual Redis Fields

If not using REDIS_URL:

```yaml
# k8s/secrets.yaml
data:
  REDIS_HOST: cmVkaXMuaG9zdC5jb20=
  REDIS_PORT: NjM3OQ==
  REDIS_PASSWORD: cmVkaXNfcGFzc3dvcmQ=
```

## Useful Commands Cheat Sheet

```bash
# Get all resources in namespace
kubectl get all -n code-talk

# Delete all resources
kubectl delete namespace code-talk

# Restart deployment
kubectl rollout restart deployment/code-talk-server -n code-talk

# Shell into pod
kubectl exec -it <pod-name> -n code-talk -- /bin/sh

# Copy files from pod
kubectl cp code-talk/<pod-name>:/path/to/file ./local-file

# View resource usage
kubectl top pods -n code-talk
kubectl top nodes

# Get pod YAML
kubectl get pod <pod-name> -n code-talk -o yaml

# Apply all manifests
kubectl apply -f k8s/

# Delete all manifests
kubectl delete -f k8s/
```

## Next Steps

- Set up continuous deployment from GitHub Actions
- Configure monitoring and alerting (Prometheus/Grafana)
- Set up centralized logging (ELK, Loki)
- Configure backup strategy for external databases
- Set up staging environment
- Load testing and optimization
- Consider service mesh (Istio/Linkerd) for advanced features

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Neon Documentation](https://neon.tech/docs/)
- [Upstash Documentation](https://docs.upstash.com/)
- [Docker Deployment Guide](./DOCKER.md)
- [CI/CD Pipeline Guide](./CICD.md)
