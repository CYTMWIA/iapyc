from ...core import Host, operation
from .. import pacman
from .utils import sudo_pacman_disable_password, sudo_pacman_enable_password


@operation
def setup(host: Host):
    if is_installed():
        print("yay already installed")
        return

    pacman.install(packages=["git", "base-devel"])

    host.run("rm -rf yay-bin && git clone https://aur.archlinux.org/yay-bin.git")

    sudo_pacman_disable_password()

    # 运行到最后会调用 sudo，所以提前修改 sudoers 文件
    host.run("cd yay-bin && makepkg -si --noconfirm")

    sudo_pacman_enable_password()


@operation
def is_installed(host: Host):
    which = host.run("which yay", raise_for_failure=False)
    return bool(len(which.stdout.strip()))
