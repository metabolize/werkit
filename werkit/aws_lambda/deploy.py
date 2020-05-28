import os
import zipfile
from shutil import copyfile, copytree, rmtree
import venv
from executor import execute


# https://stackoverflow.com/a/1855118/366856
def zipdir(path, ziph, start_path="."):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            fullpath = os.path.join(root, file)
            arcname = os.path.relpath(fullpath, start=start_path)
            ziph.write(fullpath, arcname=arcname)


def _clean(build_dir):
    rmtree(build_dir, ignore_errors=True)


def build_orchestrator_zip(build_dir, path_to_zipfile):
    venv_dir = os.path.join(build_dir, "venv")
    zip_dir = os.path.join(build_dir, "zip")
    source_dir = os.path.dirname(os.path.dirname(__file__))

    if os.path.isdir(build_dir):
        _clean(build_dir)

    os.makedirs(zip_dir, exist_ok=True)

    copytree(source_dir, os.path.join(zip_dir, "werkit"))

    venv.create(venv_dir, with_pip=True)
    path_to_venv_python = os.path.join(venv_dir, "bin", "python")
    execute(path_to_venv_python, "-m", "pip", "install", "--upgrade", "pip")
    execute(path_to_venv_python, "-m", "pip", "install", "wheel")
    execute(
        path_to_venv_python, "-m", "pip", "install", "-r", "requirements.txt",
    )
    site_packages_dir = os.path.join(venv_dir, "lib64", "python3.7", "site-packages")
    if not os.path.exists(site_packages_dir):
        site_packages_dir = os.path.join(venv_dir, "lib", "python3.7", "site-packages")

    for f in os.listdir(site_packages_dir):
        src = os.path.join(site_packages_dir, f)
        dest = os.path.join(zip_dir, f)
        if os.path.isfile(src):
            copyfile(src, dest)
        else:
            copytree(src, dest)

    # create the orchestrator function
    zipf = zipfile.ZipFile(
        path_to_zipfile, "w", zipfile.ZIP_DEFLATED
    )  # TODO: make this a tempfile
    zipdir(zip_dir, zipf, zip_dir)
    zipf.close()


def create_orchestrator_function(
    role,
    path_to_orchestrator_zip,
    client,
    worker_function_name,
    orchestrator_function_name,
    worker_timeout=None,
    orchestrator_timeout=600,
):
    environment = {"Variables": {"LAMBDA_WORKER_FUNCTION_NAME": worker_function_name}}

    if worker_timeout:
        environment["Variables"]["LAMBDA_WORKER_TIMEOUT"] = str(worker_timeout)

    with open(path_to_orchestrator_zip, "rb") as f:
        zipfile_contents = f.read()

    return client.create_function(
        FunctionName=orchestrator_function_name,
        Runtime="python3.7",
        Role=role,
        Handler="werkit.aws_lambda.default_handler.handler",
        Code={"ZipFile": zipfile_contents},
        Environment=environment,
        Timeout=orchestrator_timeout,
    )
