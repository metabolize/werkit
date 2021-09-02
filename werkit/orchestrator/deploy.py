import os
from werkit.aws_lambda.build import (
    collect_zipfile_contents,
    create_venv_with_dependencies,
    create_zipfile_from_dir,
    export_poetry_requirements,
)
from werkit.aws_lambda.deploy import perform_create, perform_update_code


def prepare_zip_file(build_dir, path_to_orchestrator_zip):
    if os.path.isdir(build_dir):
        raise ValueError(f"build_dir should not exist: {build_dir}")

    os.makedirs(build_dir)

    venv_dir = os.path.join(build_dir, "venv")
    zip_dir = os.path.join(build_dir, "zip")
    exported_requirements = os.path.join(build_dir, "requirements.txt")
    export_poetry_requirements(
        output_file=exported_requirements, extras=["lambda_common"]
    )

    create_venv_with_dependencies(
        venv_dir, install_requirements_from=[exported_requirements]
    )
    collect_zipfile_contents(
        target_dir=zip_dir, venv_dir=venv_dir, src_files=[], src_dirs=["werkit"]
    )
    create_zipfile_from_dir(dir_path=zip_dir, path_to_zipfile=path_to_orchestrator_zip)


def deploy_orchestrator(
    aws_region,
    build_dir,
    path_to_orchestrator_zip,
    orchestrator_function_name,
    role,
    worker_function_name,
    worker_timeout,
    s3_code_bucket=None,
    orchestrator_timeout=600,
    verbose=False,
):
    prepare_zip_file(build_dir, path_to_orchestrator_zip)
    env_vars = {"LAMBDA_WORKER_FUNCTION_NAME": worker_function_name}
    if worker_timeout:
        env_vars["LAMBDA_WORKER_TIMEOUT"] = str(worker_timeout)

    perform_create(
        aws_region=aws_region,
        local_path_to_zipfile=path_to_orchestrator_zip,
        handler="werkit.orchestrator.orchestrator_lambda.handler.handler",
        function_name=orchestrator_function_name,
        role=role,
        timeout=orchestrator_timeout,
        memory_size=3008,  # maximum lambda memory
        env_vars=env_vars,
        s3_code_bucket=s3_code_bucket,
        verbose=verbose,
    )


def update_orchestrator_code(
    aws_region,
    build_dir,
    path_to_orchestrator_zip,
    orchestrator_function_name,
    s3_code_bucket=None,
    verbose=False,
):
    prepare_zip_file(build_dir, path_to_orchestrator_zip)

    perform_update_code(
        aws_region=aws_region,
        local_path_to_zipfile=path_to_orchestrator_zip,
        function_name=orchestrator_function_name,
        s3_code_bucket=s3_code_bucket,
        verbose=verbose,
    )
