# Ansible Playbook Guide

This guide provides instructions on how to create and work with Ansible playbooks using the latest version of Ansible.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## install docker on almalinux 9
```shell
sudo dnf --refresh update
sudo dnf upgrade
sudo reboot
sudo dnf -y install yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker 
sudo systemctl enable  docker 
sudo systemctl status  docker 
sudo docker version
sudo usermod -aG docker $USER
echo fs.inotify.max_user_instances = 256 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
# close pycharm 
docker ps
```

## Build and Run
Docker containers that uses for Ansible role and playbook testing.
```shell
git clone  https://github.com/crunchy-devops/ansible-fgtech.git
cd ansible-fgtech
```

### Supported tags and platforms

Alma Linux:


- `almalinux-9` (`linux/amd64`,`linux/arm64`)


Fedora:

- `fedora-41` (`linux/amd64`,`linux/arm64`)

Ubuntu:

- `ubuntu-24.04` (`linux/amd64`,`linux/arm64`)

### Usage

#### With Molecule

```yaml
---
dependency:
  name: 'galaxy'
  enabled: true
driver:
  name: 'docker'
platforms:
  - name: 'instance-ubuntu'
    image: 'antmelekhin/docker-systemd:ubuntu-22.04'
    volumes:
      - '/sys/fs/cgroup:/sys/fs/cgroup:rw'
      - '/var/lib/containerd'
    cgroupns_mode: 'host'
    privileged: true
    pre_build_image: true
    groups:
      - 'debian_family'
  - name: 'instance-rocky'
    image: 'antmelekhin/docker-systemd:rockylinux-9'
    volumes:
      - '/sys/fs/cgroup:/sys/fs/cgroup:rw'
      - '/var/lib/containerd'
    cgroupns_mode: 'host'
    privileged: true
    pre_build_image: true
    groups:
      - 'rhel_family'
provisioner:
  name: 'ansible'
verifier:
  name: 'ansible'
```

#### Build and run

- Build the image with `Ubuntu 24.04`

  ```bash
export DISTR='centos'
export VERSION='7'
export KEY_CONTENT=$(cat ~/.ssh/id_rsa.pub)
docker build --build-arg SSH_PUBLIC_KEY="${KEY_CONTENT}" -t docker-systemd:${DISTR}-${VERSION} -f ${DISTR}/${VERSION}.Dockerfile .

export DISTR='alpine'
export VERSION='3.18'
docker build --build-arg SSH_PUBLIC_KEY="${KEY_CONTENT}" -t docker-systemd:${DISTR}-${VERSION} -f ${DISTR}/${VERSION}.Dockerfile .

export DISTR='ubuntu'
export VERSION='24.04'
docker build --build-arg SSH_PUBLIC_KEY="${KEY_CONTENT}" -t docker-systemd:${DISTR}-${VERSION} -f ${DISTR}/${VERSION}.Dockerfile .

export DISTR='almalinux'
export VERSION='10'
export KEY_CONTENT=$(cat ~/.ssh/id_rsa.pub)
docker build --build-arg SSH_PUBLIC_KEY="${KEY_CONTENT}" -t docker-systemd:${DISTR}-${VERSION} -f ${DISTR}/${VERSION}.Dockerfile .

  ```

- Run the container

  ```bash
  docker run -d --name systemd-${DISTR}-${VERSION} --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:rw  --hostname=${DISTR}.home --cgroupns=host docker-systemd:${DISTR}-${VERSION}
  ```

- Enter to the container

  ```bash
  docker exec -it systemd-${DISTR}-${VERSION} /bin/bash
  ```

- Remove the container

  ```bash
  docker rm -f systemd-${DISTR}-${VERSION}
  ```

## Installation

1. Install Ansible using pip (recommended for the latest version):
   ```bash
   python -m pip install --user ansible
   ```

2. Verify the installation:
   ```bash
   ansible --version
   ```

## Creating Your First Playbook

1. Create a new directory structure for your playbook:
   ```
   your_playbook/
   ├── inventory/
   │   └── hosts.ini
   ├── group_vars/
   │   └── all.yml
   ├── roles/
   │   └── common/
   │       ├── tasks/
   │       │   └── main.yml
   │       └── handlers/
   │           └── main.yml
   └── playbook.yml
   ```

2. Create an inventory file (`inventory/hosts.ini`):
   ```ini
   [web_servers]
   server1.example.com
   server2.example.com

   [db_servers]
   dbserver.example.com

   [all:vars]
   ansible_python_interpreter=/usr/bin/python3
   ```

3. Create a basic playbook (`playbook.yml`):
   ```yaml
   ---
   - name: My First Playbook
     hosts: all
     become: true
     gather_facts: true

     tasks:
       - name: Ensure packages are installed
         package:
           name: ["tree", "htop", "git"]
           state: present
         when: ansible_os_family == 'Debian'
   ```

## Best Practices

1. **Use Roles**: Organize your playbooks using roles for better reusability.
2. **Use Variables**: Store variables in `group_vars/` and `host_vars/` directories.
3. **Use Tags**: Tag your tasks for selective execution.
4. **Use Handlers**: For tasks that need to be triggered by other tasks.
5. **Documentation**: Use comments and README files to document your playbooks.

## Example Role Structure

```yaml
# roles/example/tasks/main.yml
- name: Install packages
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ packages }}"
  tags: [packages]

- name: Ensure service is running
  service:
    name: nginx
    state: started
    enabled: true
  tags: [service]
```

## Running Playbooks

```bash
# Basic playbook execution
ansible-playbook -i inventory/hosts.ini playbook.yml

# Run with tags
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "packages"

# Run with extra variables
ansible-playbook -i inventory/hosts.ini playbook.yml -e "variable=value"

# Check syntax
ansible-playbook --syntax-check playbook.yml

# Run in check mode (dry run)
ansible-playbook -i inventory/hosts.ini --check playbook.yml
```

## Useful Ansible Commands

- List all hosts in inventory:
  ```bash
  ansible all -i inventory/hosts.ini --list-hosts
  ```

- Ping all hosts:
  ```bash
  ansible all -i inventory/hosts.ini -m ping
  ```

- Run ad-hoc command:
  ```bash
  ansible all -i inventory/hosts.ini -a "uptime"
  ```

## Documentation and Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)


## Install python virutal env on almalinux
```aiexclude
sudo dnf update -y 
sudo dnf install -y python3.13
sudo dnf install -y python3.13-pip 
python3 --version
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1
sudo alternatives --config python3
python3 --version
python3 -m venv venv
source venv/bin/activate
pip3 install docker
pip3 install --upgrade pip
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
