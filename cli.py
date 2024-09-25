import click
import utils
import setup

@click.group()
def cli():
    """CLI tool for managing Kind clusters."""
    pass

@cli.command()
@click.option('--config', default='https://raw.githubusercontent.com/finnegan1/K8s-Demo/main/three_node_config.yaml', help='Path to the Kind cluster configuration file.')
def create(config):
    """Create and set up a Kind cluster."""
    click.echo("Creating and setting up the Kind cluster...")
    # Step 1: Set up Kind cluster
    utils.execute_command(["kind", "create", "cluster", "--config", config])

    # Step 2: Build and load Docker image
    utils.execute_command(["docker", "build", "-t", "webapp:latest", "."])
    utils.execute_command(["kind", "load", "docker-image", "webapp:latest"])

    # Step 3: Apply Kubernetes configurations
    utils.execute_command(["kubectl", "apply", "-f", "metrics-server.yaml"])
    utils.execute_command(["kubectl", "apply", "-f", "webapp-deployment.yaml"])
    utils.execute_command(["kubectl", "apply", "-f", "webapp-hpa.yaml"])
    utils.execute_command(["kubectl", "apply", "-f", "https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml"])

    # Step 4: Wait for pods to be ready
    utils.execute_command(["kubectl", "wait", "--for=condition=Ready", "pods", "--all", "--timeout=300s"])

    # Set up dashboard access
    utils.execute_command(["kubectl", "create", "serviceaccount", "dashboard-admin", "-n", "kubernetes-dashboard"])
    utils.execute_command([
        "kubectl", "create", "clusterrolebinding", "dashboard-admin-binding",
        "--clusterrole=cluster-admin",
        "--serviceaccount=kubernetes-dashboard:dashboard-admin"
    ])

    token = utils.execute_command(["kubectl", "-n", "kubernetes-dashboard", "create", "token", "dashboard-admin"])
    click.echo(f"Dashboard token: {token}")

    utils.kill_process_on_port(8001)
    utils.start_subprocess(["kubectl", "proxy"])
    click.echo("Dashboard is running at http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/")

@cli.command()
def delete():
    """Delete the Kind cluster."""
    click.echo("Deleting the Kind cluster...")
    utils.execute_command(["kind", "delete", "cluster"])
    utils.kill_process_on_port(8001)
    click.echo("Kind cluster deleted successfully.")

if __name__ == '__main__':
    cli()
