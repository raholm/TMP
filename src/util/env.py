import os


def get_env_variable(variable):
    return os.environ[variable]


def get_project_path():
    return get_env_variable("TMP_PATH")
