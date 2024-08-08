from ...core import Host, operation

SUDO_CFG = "/etc/sudoers.d/pacman_tmp"


@operation
def sudo_pacman_disable_password(host: Host):
    pacman_path = host.run("which pacman").stdout.strip()

    host.sudo("mkdir -p /etc/sudoers.d")

    # Cannot echo "hello" > x.txt even with sudo? - Ask Ubuntu
    # https://askubuntu.com/questions/103643/cannot-echo-hello-x-txt-even-with-sudo
    # The redirection is done by the shell before sudo is even started.
    host.sudo(f"echo \"ALL ALL=NOPASSWD: {pacman_path}\" > {SUDO_CFG}")


@operation
def sudo_pacman_enable_password(host: Host):
    host.sudo(f"rm -f {SUDO_CFG}")
