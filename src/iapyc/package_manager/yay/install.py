from ...core import Host, operation
from .setup import setup
from .utils import sudo_pacman_disable_password, sudo_pacman_enable_password


@operation
def install(host: Host, packages: str | list[str]):
    setup()

    if isinstance(packages, str):
        packages = [packages]
    pkgs_s = " ".join(packages)

    sudo_pacman_disable_password()  # 预防可能的输密码环节
    host.run(f"yay -Sy --noconfirm --needed {pkgs_s}", hide=False)
    sudo_pacman_enable_password()
