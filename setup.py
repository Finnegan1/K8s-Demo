import ipywidgets as widgets
from IPython.display import display
import utils

def setup(config):
    print(f"Setting up Kind cluster with config: {config}")
    # Step 1: Set up Kind cluster
    utils.execute_command(
        [
            "kind",
            "create",
            "cluster",
            "--config",
            config
        ]
    )
    print("Kind cluster created successfully")

    # Step 2: Build and load Docker image
    utils.execute_command(
        ["docker", "build", "-t", "webapp:latest", "."]
    )
    utils.execute_command(
        ["kind", "load", "docker-image", "webapp:latest"]
    )

    # Step 3: Apply Kubernetes configurations
    utils.execute_command(
        ["kubectl", "apply", "-f", "https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/metrics-server.yaml"]
    )
    utils.execute_command(
        ["kubectl", "apply", "-f", "https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-deployment.yaml"]
    )
    utils.execute_command(
        ["kubectl", "apply", "-f", "https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/webapp-hpa.yaml"]
    )
    utils.execute_command(
        ["kubectl", "apply", "-f", "https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml"]
    )

    # Step 4: Wait for pods to be ready
    output = utils.execute_command(
        ["kubectl", "wait", "--for=condition=Ready", "pods", "--all", "--timeout=300s"]
    )

    output = utils.execute_command(
        ["kubectl", "get", "pods"]
    )
    print(output)

    output = utils.execute_command(
        ["kubectl", "get", "services"]
    )
    print(output)

    utils.execute_command(
        ["kubectl", "create", "serviceaccount", "dashboard-admin", "-n", "kubernetes-dashboard"]
    )
    utils.execute_command(
        ["kubectl", "create", "clusterrolebinding", "dashboard-admin-binding",
         "--clusterrole=cluster-admin",
         "--serviceaccount=kubernetes-dashboard:dashboard-admin"]
    )

    token = utils.execute_command(
        ["kubectl", "-n", "kubernetes-dashboard", "create", "token", "dashboard-admin"]
    )

    utils.kill_process_on_port(8001)
    utils.start_subprocess(
        ["kubectl", "proxy"]
    )
    return token