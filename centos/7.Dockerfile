FROM centos:7

LABEL maintainer='Anton Melekhin'

ENV container=docker
ARG SSH_PUBLIC_KEY
# 1. Copier le script d'entrée
COPY centos/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN INSTALL_PKGS='findutils initscripts iproute git openssh-client epel-release vim sudo openssh-server ' \
    && sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^#.*baseurl=http/baseurl=http/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^mirrorlist=http/#mirrorlist=http/g' /etc/yum.repos.d/*.repo \
    && yum makecache fast && yum install -y $INSTALL_PKGS \
    \
    && curl --silent 'https://copr.fedorainfracloud.org/coprs/jsynacek/systemd-backports-for-centos-7/repo/epel-7/jsynacek-systemd-backports-for-centos-7-epel-7.repo' --output /etc/yum.repos.d/jsynacek-systemd-centos-7.repo \
    && yum makecache fast && yum update -y \
    && yum clean all

RUN yum install -y ansible && localedef -i en_US -f UTF-8 en_US.UTF-8

RUN rpm -Uvh https://repo.zabbix.com/zabbix/7.4/release/rhel/7/noarch/zabbix-release-latest-7.4.el7.noarch.rpm \
    && yum install -y zabbix-sender zabbix-agent

RUN yum groupinstall -y "Development tools"

RUN yum install -y python2-pip python2-devel cronie

RUN useradd -m ansible && echo "ansible:12345678" | chpasswd && \
    echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    usermod -aG wheel ansible

USER ansible
WORKDIR /home/ansible
RUN mkdir -p /home/ansible/.ssh

# Injecter la variable dans le fichier authorized_keys
RUN echo "${SSH_PUBLIC_KEY}" >> /home/ansible/.ssh/authorized_keys \
    && chmod 600 /home/ansible/.ssh/authorized_keys \
    && chown ansible:ansible /home/ansible/.ssh/authorized_keys

USER root
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -print0 | xargs -0 rm -vf


VOLUME [ "/sys/fs/cgroup" ]
# 2. Définir le script comme ENTRYPOINT
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
#ENTRYPOINT [ "/usr/sbin/init" ]

# 3. Utiliser CMD pour passer des arguments au script (ici, les services à démarrer)
# Nous passons 'sshd.service' comme service à démarrer.
CMD ["sshd.service"]