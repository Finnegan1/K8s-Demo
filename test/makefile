
# Variables
KUBECTL = kubectl
PROXY_PORT = 8001
WEBAPP_PORT = 8080
TOKEN_COMMAND = pbcopy

# Phony targets
.PHONY: create-cluster delete-cluster image apply-resources dashboard-credentials proxy clean help kill-proxy webapp-port-forward watch-hpa demo-full demo-partial setup
# Default target
all: help


#########################################################
# Create cluster
#########################################################
create-cluster:
	curl -O https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/three_node_config.yaml && kind create cluster --config three_node_config.yaml


#########################################################
# Build and load image
#########################################################
image:
	docker build -t webapp:latest .
	kind load docker-image webapp:latest


#########################################################
# Apply resources
#########################################################
apply-resources:
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/metrics-server.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-deployment.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-hpa.yaml
	$(KUBECTL) apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
	$(KUBECTL) wait --for=condition=Ready pods --all --timeout=300s


#########################################################
# Clean up
#########################################################
clean:
	kind delete cluster


#########################################################
# Watch HPA
#########################################################
watch-hpa:
	watch -n 1 $(KUBECTL) get hpa webapp-hpa

#########################################################
# Proxy and port forwarding (dashboard)
#########################################################
kill-proxy:
	@PID=$$(lsof -ti:$(PROXY_PORT)); \
	if [ -z "$$PID" ]; then \
		echo "No process found using port $(PROXY_PORT)"; \
	else \
		echo "Killing process $$PID using port $(PROXY_PORT)"; \
		kill -9 $$PID; \
		echo "Process killed successfully"; \
	fi
proxy: kill-proxy
	$(KUBECTL) proxy --port=$(PROXY_PORT) &
webapp-port-forward:
	$(KUBECTL) port-forward service/webapp-service $(WEBAPP_PORT):80 &
open-dashboard:
	$(KUBECTL) create serviceaccount dashboard-admin -n kubernetes-dashboard
	$(KUBECTL) create clusterrolebinding dashboard-admin-binding \
		--clusterrole=cluster-admin \
		--serviceaccount=kubernetes-dashboard:dashboard-admin
	$(KUBECTL) -n kubernetes-dashboard create token dashboard-admin | pbcopy
	@open http://localhost:$(PROXY_PORT)/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
run-fowrards:
	@parallel ::: 'make proxy' 'make webapp-port-forward' 'make open-dashboard'



#########################################################
# Load testing
#########################################################

# Full load test (10 concurrent users)
demo-full:
	ab -n 100000 -c 10 http://localhost:$(WEBAPP_PORT)/
# Partial load test (3 concurrent users)
demo-partial:
	ab -n 100000 -c 3 http://localhost:$(WEBAPP_PORT)/

setup: create-cluster image apply-resources run-fowrards watch-hpa