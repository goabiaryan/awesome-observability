# Production Deployment Guide for LLM Observability

## 🚀 Deployment Checklist

Before deploying to production, ensure:

- [ ] All API keys and secrets are in environment variables (not in code)
- [ ] Database backups are configured
- [ ] SSL/TLS certificates are set up
- [ ] Monitoring and alerting are enabled
- [ ] Log aggregation is configured
- [ ] Resource limits are set
- [ ] Network policies are in place

## 🐳 Docker Deployment

### 1. Build Docker Image

```bash
docker build -t llm-observability:latest .
```

### 2. Push to Registry

```bash
# Example: Docker Hub
docker login
docker tag llm-observability:latest myusername/llm-observability:latest
docker push myusername/llm-observability:latest

# Example: AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag llm-observability:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/llm-observability:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/llm-observability:latest
```

### 3. Deploy with Docker Compose

```bash
# Production setup
docker-compose -f docker-compose.yml \
  -f docker-compose.prod.override.yml \
  up -d

# Verify all services
docker-compose ps

# View logs
docker-compose logs -f
```

## ☸️ Kubernetes Deployment

### 1. Prerequisites

```bash
kubectl cluster-info
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### 2. Create Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: llm-observability
```

```bash
kubectl apply -f k8s/namespace.yaml
```

### 3. Deploy PostgreSQL

```yaml
# k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: llm-observability
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: langfuse
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POSTGRES_DB
          value: langfuse
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: llm-observability
spec:
  ports:
  - port: 5432
  clusterIP: None
  selector:
    app: postgres
```

### 4. Deploy Langfuse

```yaml
# k8s/langfuse-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langfuse
  namespace: llm-observability
spec:
  replicas: 2  # High availability
  selector:
    matchLabels:
      app: langfuse
  template:
    metadata:
      labels:
        app: langfuse
    spec:
      containers:
      - name: langfuse
        image: ghcr.io/langfuse/langfuse:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: langfuse-secret
              key: database-url
        - name: NEXTAUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: langfuse-secret
              key: nextauth-secret
        - name: NEXTAUTH_URL
          value: "https://langfuse.example.com"
        - name: SALT
          valueFrom:
            secretKeyRef:
              name: langfuse-secret
              key: salt
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: langfuse
  namespace: llm-observability
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: langfuse
```

### 5. Deploy Prometheus & Grafana

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace llm-observability \
  --values k8s/prometheus-values.yaml

helm install grafana grafana/grafana \
  --namespace llm-observability \
  --values k8s/grafana-values.yaml
```

### 6. Deploy Your LLM Application

```yaml
# k8s/llm-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-app
  namespace: llm-observability
spec:
  replicas: 3  # Auto-scaling
  selector:
    matchLabels:
      app: llm-app
  template:
    metadata:
      labels:
        app: llm-app
    spec:
      containers:
      - name: app
        image: myregistry/llm-observability:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        - name: LANGFUSE_PUBLIC_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: langfuse-public
        - name: LANGFUSE_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: langfuse-secret
        - name: LANGFUSE_HOST
          value: "http://langfuse:3000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: llm-app
  namespace: llm-observability
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: llm-app
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-app-hpa
  namespace: llm-observability
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 7. Deploy Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-observability-ingress
  namespace: llm-observability
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    - langfuse.example.com
    - grafana.example.com
    secretName: llm-observability-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: llm-app
            port:
              number: 80
  - host: langfuse.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: langfuse
            port:
              number: 80
  - host: grafana.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 80
```

### 8. Deploy Secrets

```bash
# Create secrets
kubectl create secret generic api-keys \
  --from-literal=openai="$OPENAI_API_KEY" \
  --from-literal=langfuse-public="$LANGFUSE_PUBLIC_KEY" \
  --from-literal=langfuse-secret="$LANGFUSE_SECRET_KEY" \
  -n llm-observability

kubectl create secret generic postgres-secret \
  --from-literal=password="$(openssl rand -base64 32)" \
  -n llm-observability

kubectl create secret generic langfuse-secret \
  --from-literal=database-url="postgresql://langfuse:password@postgres:5432/langfuse" \
  --from-literal=nextauth-secret="$(openssl rand -hex 32)" \
  --from-literal=salt="$(openssl rand -hex 16)" \
  -n llm-observability
```

## 🔒 Security Best Practices

### Network Security
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: llm-observability-netpol
  namespace: llm-observability
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### Pod Security
```yaml
# k8s/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
```

## 📈 Monitoring Production Deployment

### Key Metrics to Monitor

```
- Pod CPU/Memory usage
- Database connection pool
- Request latency (P95, P99)
- Error rate
- Cost tracking
- Hallucination detection
```

### Set Up Alerts

```bash
kubectl apply -f k8s/alerts.yaml
```

## 🔄 Continuous Deployment

### GitHub Actions Example

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build image
      run: docker build -t myregistry/llm-observability:${{ github.sha }} .
    
    - name: Push image
      run: docker push myregistry/llm-observability:${{ github.sha }}
    
    - name: Deploy to K8s
      run: |
        kubectl set image deployment/llm-app \
          app=myregistry/llm-observability:${{ github.sha }} \
          -n llm-observability
```

## 📊 Production Monitoring Dashboard

Create a Grafana dashboard with:
- Pod status and resource usage
- Application performance metrics
- Database health
- Cost trends
- Alert status

## 🆘 Troubleshooting Production Issues

### Pod not starting

```bash
kubectl describe pod <pod-name> -n llm-observability
kubectl logs <pod-name> -n llm-observability
```

### Database connection issues

```bash
kubectl exec -it postgres-0 -n llm-observability -- psql -U langfuse
```

### Performance issues

```bash
kubectl top nodes
kubectl top pods -n llm-observability
```

---

**For more information, see:**
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Kubernetes documentation](https://kubernetes.io/docs/)
- [Langfuse deployment guide](https://langfuse.com/docs/deployment)
