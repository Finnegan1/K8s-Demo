# Variables
KUBECTL = kubectl
PROXY_PORT = 8001
WEBAPP_PORT = 8080

# Phony targets
.PHONY: all create-cluster delete-cluster build-image load-image apply-resources wait-for-pods dashboard token proxy clean help kill-proxy webapp-port-forward watch-hpa load-test-full load-test-partial

# Default target
all: help

# Create Kind cluster
create-cluster:
	curl -O https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/three_node_config.yaml && kind create cluster --config three_node_config.yaml

# Delete Kind cluster
delete-cluster:
	kind delete cluster

# Build Docker image
build-image:
	docker build -t webapp:latest .

# Load Docker image into Kind
load-image:
	kind load docker-image webapp:latest

# Apply Kubernetes configurations
apply-resources:
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/metrics-server.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-deployment.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-hpa.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Wait for pods to be ready
wait-for-pods:
	$(KUBECTL) wait --for=condition=Ready pods --all --timeout=300s

# Setup Kubernetes dashboard
dashboard:
	$(KUBECTL) create serviceaccount dashboard-admin -n kubernetes-dashboard
	$(KUBECTL) create clusterrolebinding dashboard-admin-binding \
		--clusterrole=cluster-admin \
		--serviceaccount=kubernetes-dashboard:dashboard-admin

# Get dashboard token
token:
	$(KUBECTL) -n kubernetes-dashboard create token dashboard-admin

# Kill process using the proxy port
kill-proxy:
	@PID=$$(lsof -ti:$(PROXY_PORT)); \
	if [ -z "$$PID" ]; then \
		echo "No process found using port $(PROXY_PORT)"; \
	else \
		echo "Killing process $$PID using port $(PROXY_PORT)"; \
		kill -9 $$PID; \
		echo "Process killed successfully"; \
	fi

# Start kubectl proxy
proxy: kill-proxy
	$(KUBECTL) proxy --port=$(PROXY_PORT)

# Port forward webapp service
webapp-port-forward:
	$(KUBECTL) port-forward service/webapp-service $(WEBAPP_PORT):80

# Clean up
clean:
	kind delete cluster

# Help
help:
	@echo "Available targets:"
	@echo "  create-cluster		: Create Kind cluster"
	@echo "  delete-cluster		: Delete Kind cluster"
	@echo "  build-image		: Build Docker image"
	@echo "  load-image			: Load Docker image into Kind"
	@echo "  apply-resources	: Apply Kubernetes configurations"
	@echo "  wait-for-pods		: Wait for pods to be ready"
	@echo "  dashboard			: Setup Kubernetes dashboard"
	@echo "  token				: Get dashboard access token"
	@echo "  proxy				: Kill existing proxy and start kubectl proxy (default port: $(PROXY_PORT))"
	@echo "  clean				: Clean up (delete cluster)"
	@echo "  all				: Display this help message"
	@echo "  kill-proxy			: Kill process using the proxy port (default: $(PROXY_PORT))"
	@echo "  webapp-port-forward: Port forward webapp service to localhost (default port: $(WEBAPP_PORT))"
	@echo "  watch-hpa			: Watch HPA status (updates every 1 second)"
	@echo "  load-test-full		: Run full load test (1000 requests, 10 concurrent users)"
	@echo "  load-test-partial	: Run partial load test (1000 requests, 3 concurrent users)"

# Full setup process
full-setup: create-cluster build-image load-image apply-resources wait-for-pods dashboard token
	@echo "Full setup completed. Run 'make proxy' to start the Kubernetes dashboard proxy."
	@echo "Access the dashboard at: http://localhost:$(PROXY_PORT)/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
	@echo "Run 'make webapp-port-forward' to port forward the webapp service to localhost:$(WEBAPP_PORT)"
	@echo "Use the token from 'make token' to log in."

# Watch HPA status
watch-hpa:
	watch -n 1 $(KUBECTL) get hpa webapp-hpa

# Full load test (10 concurrent users)
load-test-full:
	ab -n 1000 -c 10 http://localhost:$(WEBAPP_PORT)/

# Partial load test (3 concurrent users)
load-test-partial:
	ab -n 1000 -c 3 http://localhost:$(WEBAPP_PORT)/
