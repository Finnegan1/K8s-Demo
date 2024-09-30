import os
import subprocess
from rich import print
import psutil

def kill_process_on_port(port):
    # Iterate over all processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check each process's network connections
            connections = proc.connections(kind='inet')
            for conn in connections:
                # Check if the process is listening on the specified port
                if conn.laddr.port == port:
                    print(f"Killing process {proc.info['name']} with PID {proc.info['pid']} using port {port}")
                    proc.kill()  # Terminate the process
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Handle processes that no longer exist or can't be accessed
            continue


def pretty_print_command_output(command: list[str], output: str):
    """
    Pretty prints the command output.

    :param command: The command that was executed
    :param cwd: The current working directory
    :param output: The command output as a string
    """
    print(f"[bold cyan]Command:[/bold cyan] {command}")
    print(f"[bold cyan]Output:[/bold cyan] {output}")
    print("\n")


def execute_command(command, cwd: str|None = None, print_output: bool = True):
    """
    Executes a command and waits for the result.

    :param command: The command to execute as a list of strings (e.g., ['ls', '-la'])
    :return: The command output as a string
    """
    if not cwd:
        cwd = os.getcwd()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
        if print_output:
            pretty_print_command_output(command, result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"


def start_subprocess(command, cwd: str = None, print_output: bool = False):
    """
    Starts a subprocess without waiting for it to finish.

    :param command: The command to start as a list of strings (e.g., ['python', 'script.py'])
    :return: The subprocess object
    """
    if not cwd:
        cwd = os.getcwd()

    try:
        process = subprocess.Popen(command, cwd=os.getcwd())
        if print_output:
            pretty_print_command_output(command, "Subprocess started")
        return process
    except Exception as e:
        print(f"Failed to start subprocess: {e}")
