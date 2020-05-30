import os
import zipfile
from shutil import copyfile, copytree, rmtree
import venv
from executor import execute
from .deploy import perform_create


def _clean(build_dir):
    rmtree(build_dir, ignore_errors=True)


def create_venv_with_dependencies(
    venv_dir,
    upgrade_pip=True,
    install_wheel=True,
    install_werkit=False,
    install_requirements=True,
    environment={},
):
    venv.create(venv_dir, with_pip=True)
    python = os.path.join(venv_dir, "bin", "python")

    if upgrade_pip:
        execute(
            python, "-m", "pip", "install", "--upgrade", "pip", environment=environment
        )

    if install_wheel:
        execute(python, "-m", "pip", "install" "wheel", environment=environment)

    if install_werkit:
        execute(
            python,
            "-m",
            "pip",
            "install"
            "werkit@git+https://github.com/metabolize/werkit.git@deploy-utils",
            environment=environment,
        )

    if install_requirements:
        execute(
            python,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            environment=environment,
        )


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

    create_zipfile_from_dir(dir_path=zip_dir, path_to_zipfile=path_to_zipfile)


def create_zipfile_from_dir(dir_path, path_to_zipfile):
    with zipfile.ZipFile(path_to_zipfile, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                fullpath = os.path.join(root, file)
                arcname = os.path.relpath(fullpath, start=dir_path)
                f.write(fullpath, arcname=arcname)
