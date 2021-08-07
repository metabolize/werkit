import os
import shutil
import sys
import venv
import zipfile
from executor import execute


def export_poetry_requirements(
    output_file, extras=[], with_credentials=True, with_hashes=True
):
    args = ["poetry", "export", "--output", output_file]
    if with_credentials:
        args.append("--with-credentials")
    if not with_hashes:
        args.append("--without-hashes")
    for extra in extras:
        args += ["--extras", extra]
    execute(*args)


def create_venv_with_dependencies(
    venv_dir,
    upgrade_pip=True,
    install_wheel=True,
    install_requirements_from=["requirements.txt"],
    install_transitive_dependencies=True,
    environment={},
):
    venv.create(venv_dir, with_pip=True)
    python = os.path.join(venv_dir, "bin", "python")

    if upgrade_pip:
        execute(
            python, "-m", "pip", "install", "--upgrade", "pip", environment=environment
        )

    if install_wheel:
        execute(python, "-m", "pip", "install", "wheel", environment=environment)

    if len(install_requirements_from) > 0:
        args = [python, "-m", "pip", "install"]
        if not install_transitive_dependencies:
            args += ["--no-dependencies"]
        for requirements_file in install_requirements_from:
            args += ["-r", requirements_file]
        execute(*args, environment=environment)


def find_site_packages_dir(venv_dir):
    for candidate_result in [
        os.path.join(venv_dir, "lib64", "python3.8", "site-packages"),
        os.path.join(venv_dir, "lib", "python3.8", "site-packages"),
        os.path.join(venv_dir, "lib64", "python3.7", "site-packages"),
        os.path.join(venv_dir, "lib", "python3.7", "site-packages"),
    ]:
        if os.path.exists(candidate_result):
            return candidate_result
    raise ValueError(f"Unable to locate site-packages folder in {venv_dir}")


def collect_zipfile_contents(
    target_dir, venv_dir, src_files=[], src_dirs=[], lib_files=[], verbose=False
):
    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    if os.path.isdir(target_dir):
        raise ValueError(f"target_dir should not exist: {target_dir}")
    if not os.path.isdir(venv_dir):
        raise ValueError(f"venv_dir should already be populated: {venv_dir}")

    # Copy dependencies from venv.
    site_packages_dir = find_site_packages_dir(venv_dir)
    pif(f"Copying dependencies from {site_packages_dir} to {target_dir}")
    shutil.copytree(site_packages_dir, target_dir)

    if lib_files:
        lib_dir = os.path.join(target_dir, "lib")
        os.makedirs(lib_dir, exist_ok=True)
        for lib_file in lib_files:
            target = os.path.join(lib_dir, os.path.basename(lib_file))
            pif(f"Copying {lib_file} to {target}/")
            shutil.copyfile(lib_file, target)

    for src_dir in src_dirs:
        target = os.path.join(target_dir, src_dir)
        pif(f"Copying {src_dir} to {target}")
        shutil.copytree(src_dir, target)

    for src_file in src_files:
        target = os.path.join(target_dir, src_file)
        pif(f"Copying {src_file} to {target}")
        shutil.copyfile(src_file, target)


def create_zipfile_from_dir(dir_path, path_to_zipfile):
    with zipfile.ZipFile(path_to_zipfile, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                fullpath = os.path.join(root, file)
                arcname = os.path.relpath(fullpath, start=dir_path)
                f.write(fullpath, arcname=arcname)
