from ...core import Host, operation
from .setup import setup


@operation
def install(host: Host, packages: str | list[str]):
    setup()

    if isinstance(packages, str):
        packages = [packages]
    pkgs_s = " ".join(packages)
    host.sudo(f"pacman -Sy --noconfirm --needed {pkgs_s}")
