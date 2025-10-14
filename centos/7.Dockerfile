FROM centos:7

LABEL maintainer='Anton Melekhin'

ENV container=docker

# 1. Copier le script d'entrée
COPY centos/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN INSTALL_PKGS='findutils initscripts iproute  openssh-client epel-release vim sudo openssh-server ' \
    && sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^#.*baseurl=http/baseurl=http/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^mirrorlist=http/#mirrorlist=http/g' /etc/yum.repos.d/*.repo \
    && yum makecache fast && yum install -y $INSTALL_PKGS \
    \
    && curl --silent 'https://copr.fedorainfracloud.org/coprs/jsynacek/systemd-backports-for-centos-7/repo/epel-7/jsynacek-systemd-backports-for-centos-7-epel-7.repo' --output /etc/yum.repos.d/jsynacek-systemd-centos-7.repo \
    && yum makecache fast && yum update -y \
    && yum clean all \


RUN useradd -m ansible && echo "ansible:12345678" | chpasswd && \
    echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    usermod -aG wheel ansible
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