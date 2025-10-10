#!/usr/bin/env python3

import json
import subprocess
import sys


def get_docker_containers():
    """
    Retrieves the list of all active Docker containers.
    """
    try:
        output = subprocess.check_output(
            ["docker", "ps", "--format", "json"],
            universal_newlines=True
        )
        return [json.loads(line) for line in output.strip().split('\n')]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: Unable to run Docker. Is the daemon active? {e}", file=sys.stderr)
        return []


def format_for_ansible(containers):
    """
    Formats the list of containers into a JSON inventory for Ansible.
    Uses SSH for connection.
    """
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "docker_containers_ssh": {
            "hosts": [],
            "vars": {
                # Configure Ansible to use SSH for these hosts
                "ansible_connection": "ssh",
                "ansible_user": "root",
                # Path to the SSH key for authentication (secure method)
                "ansible_ssh_private_key_file": "/path/to/your/ssh_key"
            }
        }
    }

    for container in containers:
        host_name = container["Names"]
        inventory["docker_containers_ssh"]["hosts"].append(host_name)

        # Get the container's IP address for the SSH connection
        ip_address = subprocess.check_output(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container["ID"]],
            universal_newlines=True
        ).strip()

        # Set the IP address as the connection host
        inventory["_meta"]["hostvars"][host_name] = {
            "ansible_host": ip_address
        }

    return inventory


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        containers = get_docker_containers()
        ansible_inventory = format_for_ansible(containers)
        print(json.dumps(ansible_inventory, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == '--host':
        print(json.dumps({}))
    else:
        print("Usage: ./docker_inventory.py --list", file=sys.stderr)