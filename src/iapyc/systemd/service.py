from enum import Flag, auto

from ..core import Host, operation


class ServiceState(Flag):
    DISABLE = auto()
    ENABLE = auto()

    START = auto()
    STOP = auto()
    RELOAD = auto()
    RESTART = auto()

    def __str__(self) -> str:
        return self.name


@operation
def service(host: Host, service: str, state: str):
    for S in ServiceState:
        if S & state:
            cmd = str(S).lower()
            host.sudo(f"systemctl {cmd} {service}")
