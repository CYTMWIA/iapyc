import ansible.parsing.vault as ansible_vault


def is_encrypted(data):
    return ansible_vault.is_encrypted(data)


class FileSecret(ansible_vault.VaultSecret):
    def __init__(self, path: str):
        with open(path, "rb") as f:
            _bytes = f.read()
        super().__init__(_bytes)
