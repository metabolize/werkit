import os
import shutil
from .build import (
    create_venv_with_dependencies,
    collect_zipfile_contents,
    create_zipfile_from_dir,
)
from .deploy import perform_create


def deploy_orchestrator(
    build_dir,
    path_to_orchestrator_zip,
    orchestrator_function_name,
    role,
    worker_function_name,
    worker_timeout,
    orchestrator_timeout=None,
):
    if os.path.isdir(build_dir):
        raise ValueError(f"build_dir should not exist: {build_dir}")

    os.makedirs(build_dir)

    venv_dir = os.path.join(build_dir, "venv")
    zip_dir = os.path.join(build_dir, "zip")

    create_venv_with_dependencies(venv_dir)
    collect_zipfile_contents(
        target_dir=zip_dir, venv_dir=venv_dir, src_files=[], src_dirs=["werkit"],
    )
    create_zipfile_from_dir(
        dir_path=zip_dir, path_to_zipfile=path_to_orchestrator_zip,
    )

    env_vars = {"LAMBDA_WORKER_FUNCTION_NAME": worker_function_name}
    if worker_timeout:
        env_vars["LAMBDA_WORKER_TIMEOUT"] = str(worker_timeout)

    perform_create(
        path_to_zipfile=path_to_orchestrator_zip,
        handler="werkit.aws_lambda.default_handler.handler",
        function_name=orchestrator_function_name,
        role=role,
        timeout=orchestrator_timeout,
        memory_size=1792,
        env_vars=env_vars,
    )
