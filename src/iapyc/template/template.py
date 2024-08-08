import io
import os
import random

import jinja2
from paramiko.sftp_client import SFTPClient

from .. import fs
from ..core import Host, operation


def render(template_path: str, vars: dict):
    template_dir = os.path.dirname(template_path)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template_name = os.path.basename(template_path)
    tem = env.get_template(template_name)
    return tem.render(vars)


@operation
def template(
    host: Host,
    local_template_path: str,
    remote_dest_path: str,
    template_vars: dict,
):
    jinja_res = render(local_template_path, template_vars)

    # To avoid SFTP user has no permission to dir
    # 1. transfer to /tmp
    # 2. mv to dest by doing sudo

    tmp_filename = str(random.randint(1000000000,10000000000-1))
    tmp_path = os.path.join("/tmp", tmp_filename)
    sftp: SFTPClient = host.connection().sftp()
    sftp.putfo(io.BytesIO(jinja_res.encode("utf-8")), tmp_path)

    if fs.is_dir_exists(path=remote_dest_path):
        filename = os.path.basename(local_template_path)
        remote_dest_path = os.path.join(remote_dest_path, filename)
    print("remote_dest_path:", remote_dest_path)

    host.sudo(f"mv -f {tmp_path} {remote_dest_path}")
