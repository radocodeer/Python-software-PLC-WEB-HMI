def get_tag_by_path(root, path: str):
    parts = path.split(".")
    node = root

    for p in parts:
        node = getattr(node, p)

    return node


def set_tag_by_path(root, path: str, value):
    parts = path.split(".")
    node = root

    for p in parts[:-1]:
        node = getattr(node, p)

    setattr(node, parts[-1], value)