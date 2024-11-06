import os, re, sys

def read_file(relative_path, **kwargs):
    absolute_path = get_abs_path(relative_path)  # Construct the absolute path to the target file

    # Specify encoding='utf-8' to avoid UnicodeDecodeError
    with open(absolute_path, 'r', encoding='utf-8') as f:
        content = remove_code_fences(f.read())

    # Replace placeholders with values from kwargs
    for key, value in kwargs.items():
        placeholder = "{{" + key + "}}"
        strval = str(value)
        content = content.replace(placeholder, strval)

    return content


def remove_code_fences(text):
    return re.sub(r'~~~\w*\n|~~~', '', text)

def get_abs_path(*relative_paths):
    path = os.path.join(get_base_dir(), *relative_paths)
    return path

def exists(*relative_paths):
    path = get_abs_path(*relative_paths)
    return os.path.exists(path)

def get_base_dir():
    # Get the base directory from the current file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return base_dir
