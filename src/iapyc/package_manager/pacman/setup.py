from ...core import Host, operation


ALREADY_SETUP = set()

MIRRORS = {
    "BFSU": "https://mirrors.bfsu.edu.cn/archlinux/$repo/os/$arch",
}


@operation
def setup(host: Host):
    if host.name in ALREADY_SETUP:
        return

    if host.in_group("china"):
        use_mirror(url=MIRRORS["BFSU"])

    ALREADY_SETUP.add(host.name)


@operation
def use_mirror(host: Host, url: str):
    mirrorlist_path = "/etc/pacman.d/mirrorlist"
    mirrorlist = host.sudo(f"cat {mirrorlist_path}").stdout.splitlines()
    mirrorlist = map(lambda s: s.strip(), mirrorlist)

    top_server = ""
    for line in mirrorlist:
        if line.startswith("Server"):
            top_server = line.split()[2]
            break

    if top_server != url:
        # 转义
        url = url.replace("/", "\\/").replace(".", "\\.").replace("$", "\\$")
        # 插入镜像链接到文件头部
        host.sudo(f"sed -i \"1s/^/Server = {url}\\n/\" {mirrorlist_path}")
        # 更新缓存
        host.sudo("pacman -Syyu")
