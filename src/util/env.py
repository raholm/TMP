import os


def get_env_variable(variable):
    return os.environ[variable]


def get_project_path():
    return get_env_variable("TMP_PATH")


def get_project_data_path():
    return os.path.join(get_project_path(), "data")


def get_project_model_path():
    return os.path.join(get_project_path(), "models")
