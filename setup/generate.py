#!/usr/bin/env python3
import subprocess
import sys
import os
import time  # Import the time module

# --- Configuration ---
NUM_CONTAINERS = 5
IMAGE_NAME = "docker-systemd:almalinux-9"
BASE_NAME_TEMPLATE = "systemd-{}"
HOSTNAME_TEMPLATE = "{}.home"
HOSTS_FILE = "/etc/hosts"


def run_command(command, capture_output=False):
    """
    Executes a shell command and handles errors.

    Args:
        command (list): The command to execute as a list of strings.
        capture_output (bool): If True, captures and returns stdout.

    Returns:
        tuple: (success, output)
               success (bool): True if the command succeeded, False otherwise.
               output (str or None): The stdout if capture_output is True, else None.
    """
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return True, result.stdout.strip() if capture_output else None
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Is Docker installed and in your PATH?")
        return False, None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Return Code: {e.returncode}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        return False, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False, None


def check_if_container_exists(name):
    """Checks if a container with the given name already exists."""
    command = ["docker", "ps", "-a", "-q", "--filter", f"name=^{name}$"]
    success, output = run_command(command, capture_output=True)
    return success and output != ""


def get_container_ip(name):
    """Retrieves the IP address of a given container."""
    command = ["docker", "inspect", "-f", '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', name]
    success, ip_address = run_command(command, capture_output=True)
    return ip_address if success and ip_address else None


def update_hosts_file(ip_address, hostname):
    """Appends a new entry to the /etc/hosts file."""
    entry = f"{ip_address}\t{hostname}"
    print(f"Attempting to add entry to {HOSTS_FILE}: '{entry}'")
    try:
        with open(HOSTS_FILE, 'r') as f:
            if entry in f.read():
                print(f"Entry for {hostname} already exists in {HOSTS_FILE}. Skipping.")
                return True

        with open(HOSTS_FILE, 'a') as f:
            f.write(f"\n# Entry added by Docker script\n{entry}\n")
        print(f"Successfully added entry for {hostname} to {HOSTS_FILE}.")
        return True
    except PermissionError:
        print(f"Error: Permission denied. You must run this script with sudo to modify {HOSTS_FILE}.")
        return False
    except Exception as e:
        print(f"Failed to write to {HOSTS_FILE}: {e}")
        return False


def main():
    """
    Main function to create containers and update hosts.
    """
    # Check for root/sudo privileges, which are required to edit /etc/hosts
    if os.geteuid() != 0:
        print("This script needs to modify /etc/hosts, which requires root privileges.")
        print("Please run it with sudo: sudo python3 your_script_name.py")
        sys.exit(1)

    print(f"Starting script to generate {NUM_CONTAINERS} containers...")

    for i in range(1, NUM_CONTAINERS + 1):
        container_name = BASE_NAME_TEMPLATE.format(i)
        hostname = HOSTNAME_TEMPLATE.format(i)
        print(f"\n--- Processing Container #{i}: {container_name} ---")

        # 1. Check if the container already exists
        if check_if_container_exists(container_name):
            print(f"Container '{container_name}' already exists. Skipping creation.")
        else:
            # 2. Create the container
            docker_run_command = [
                "docker", "run", "-d",
                "--name", container_name,
                "--privileged",
                "-v", "/sys/fs/cgroup:/sys/fs/cgroup:rw",
                "--hostname", hostname,
                "--cgroupns=host",
                IMAGE_NAME
            ]
            success, _ = run_command(docker_run_command)
            if not success:
                print(f"Failed to create container '{container_name}'. Stopping script.")
                continue

                # 3. Get the container's IP address
        ip_address = get_container_ip(container_name)
        if not ip_address:
            print(f"Failed to retrieve IP for '{container_name}'. Cannot update hosts file.")
            continue

        print(f"Container '{container_name}' has IP address: {ip_address}")

        # 4. Update the /etc/hosts file
        if not update_hosts_file(ip_address, hostname):
            print(f"Failed to update hosts file for '{hostname}'.")
            continue

        # 5. Add a delay to be gentle on the Docker daemon
        print("Pausing for 1 second to avoid overloading the Docker daemon...")
        time.sleep(5)

    print(f"\n--- Script finished. ---")
    # Final check using the quiet flag as requested
    print("Running 'docker ps -q' to list running container IDs:")
    run_command(["docker", "ps", "-q"])


if __name__ == "__main__":
    main()
