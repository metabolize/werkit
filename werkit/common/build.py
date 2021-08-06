import os


def local_path_for_built_lambda(function_name):
    return os.path.join("lambdas", f"{function_name}.zip")


def local_path_for_manifest(function_name):
    return os.path.join("lambdas", f"{function_name}.manifest.json")
