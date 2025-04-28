import os


def read(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, 'w', encoding="utf-8") as f:
        f.write(content)


def path_local(path):
    return path.replace('/root/', '$HOME/')


def align_right(str_, length):
    return str_.rjust(length)


def aligned_advancement(i, total):
    l = len(str(total))
    ii = align_right(str(i+1), l)
    return f"{ii}/{total}"
