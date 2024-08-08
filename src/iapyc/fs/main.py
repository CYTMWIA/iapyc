import io
import os
import random
from enum import Enum, auto

from paramiko.sftp_client import SFTPClient

from ..core import Host, operation


class DirectoryState(Enum):
    DELETED = auto()
    EMPTY = auto()
    EXISTS = auto()


@operation
def directory(
    host: Host,
    path: str,
    state: DirectoryState,
    owner: str | None = None,
    mode: str = "755",
):
    path = path.strip()
    if owner is None:
        owner = host.run("whoami").stdout.strip()

    if state == DirectoryState.DELETED:
        host.sudo(f"rm -rf {path}")
        return

    # 创建目录
    host.sudo(f"mkdir -m {mode} -p {path}")
    host.sudo(f"chown {owner} {path}")

    if state == DirectoryState.EXISTS:
        # do nothing
        return

    if state == DirectoryState.EMPTY:
        if not path.endswith("/"):
            path += "/"
        path += "*"
        host.sudo(f"rm -rf {path}")


@operation
def is_dir_exists(host: Host, path: str):
    # dirname("/aaa/bbb/") will return "/aaa/bbb", which we don't want
    # so we have to remove endding "/" in the path
    path = path.removesuffix("/")

    ls_output = host.sudo(f"ls -l -L '{os.path.dirname(path)}'").stdout.splitlines()
    basename = os.path.basename(path)
    for line in ls_output:
        line = line.strip()
        if line.startswith("d") and line.endswith(basename):
            return True
    return False


@operation
def is_dir_empty(host: Host, path: str):
    if not is_dir_exists(path=path):
        return True

    ls_output = host.sudo(f"ls {path}").stdout.strip()
    return bool(len(ls_output))


@operation
def file(host: Host, path: str, content: None | bytes | str = None):
    path = path.removesuffix("/")
    dir_path = os.path.dirname(path)
    directory(path=dir_path, state=DirectoryState.EXISTS)

    if content is None:
        host.run(f"touch {path}")
    else:
        # To avoid SFTP user has no permission to dir
        # 1. transfer to /tmp
        # 2. mv to dest by doing sudo
        tmp_filename = str(random.randint(1000000000, 10000000000 - 1))
        tmp_path = os.path.join("/tmp", tmp_filename)

        if isinstance(content, str):
            content = content.encode("utf-8")
        sftp: SFTPClient = host.connection().sftp()
        sftp.putfo(io.BytesIO(content), tmp_path)

        host.sudo(f"mv -f {tmp_path} {path}")
