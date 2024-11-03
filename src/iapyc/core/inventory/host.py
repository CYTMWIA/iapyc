from colorama import Fore, Style
from fabric import Config, Connection, Result

from .group import Group

HOSTS_STACK = []

OPS_STACK = []


class Host:
    def __init__(self, name: str, host_vars: dict, groups: list[Group]) -> None:
        self.name = name
        self.vars = host_vars
        self.groups = groups

        self._connection = None

    def in_group(self, name: str):
        for g in self.groups:
            if g.name == name:
                return True
        return False

    def get_var(self, name: str):
        # 从 host 配置寻找
        v = self.vars.get(name, None)
        if name in self.vars:  # 若含有 name 配置项，则优先使用，哪怕是 None
            return v

        # 若 host 配置为 None ，则从 group 配置寻找
        gi = iter(self.groups)
        while v is None:
            g = next(gi, None)
            if g is None:
                break
            v = g.get_var(name)
        return v

    def _get_var_with_prefix_maybe(self, name: str, prefix: str):
        v = self.get_var(name)
        if v is None:
            v = self.get_var(prefix + name)
        return v

    def _create_connection(self):
        ssh_host = self._get_var_with_prefix_maybe("ssh_host", "ansible_")
        ssh_user = self._get_var_with_prefix_maybe("ssh_user", "ansible_")
        sudo_pass = self._get_var_with_prefix_maybe("sudo_pass", "ansible_")
        self._connection = Connection(
            host=ssh_host,
            user=ssh_user,
            config=Config(
                {
                    "sudo": {
                        "password": sudo_pass,
                    },
                }
            ),
        )

    def connection(self) -> Connection:
        if self._connection is None:
            self._create_connection()
        return self._connection

    def _command(self, func_name: str, cmd: str, raise_for_failure=True, **kwargs):
        kwargs.setdefault("hide", True)  # 隐藏输出
        kwargs.setdefault("warn", True)  # 错误时仅警告

        print(f"{func_name}: {cmd}")

        func = getattr(self.connection(), func_name)
        res: None | Result = func(cmd, **kwargs)
        if res is None:
            raise Exception("run() returned None")

        if raise_for_failure and res.failed:
            raise Exception(f"{func_name} fail: {res}")

        return res

    def run(self, cmd: str, **kwargs):
        return self._command("run", cmd, **kwargs)

    def sudo(self, cmd: str, **kwargs):
        cmd = f"bash -c '{cmd}'"
        return self._command("sudo", cmd, **kwargs)

    def __enter__(self):
        HOSTS_STACK.append(self)

    def __exit__(self, exc_type, exc_value, traceback):
        HOSTS_STACK.pop()


def current_host():
    # TODO: 多线程支持
    if len(HOSTS_STACK):
        return HOSTS_STACK[-1]
    return None


def get_operation_name(func):
    name = f"{func.__module__}.{func.__name__}"
    name = name.removeprefix("modules.")
    return name


def print_color(s):
    print(f"{Fore.CYAN}{s}{Style.RESET_ALL}")


def operation(func):
    def warpper(**kwargs):
        h = current_host()
        if h is not None:
            kwargs.setdefault("host", h)

        OPS_STACK.append(get_operation_name(func))
        print_color(f"{kwargs["host"].name} {'>'*len(OPS_STACK)} {OPS_STACK[-1]}")

        res = func(**kwargs)

        OPS_STACK.pop()
        if len(OPS_STACK):
            print_color(f"{kwargs["host"].name} {'>'*len(OPS_STACK)} {OPS_STACK[-1]}")

        return res

    return warpper
