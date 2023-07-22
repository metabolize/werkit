# Changelog

## 0.32.0

### BREAKING CHANGES

- Bump missouri dependency.

### Bug fixes

- StateManager: Eliminate some type errors downstream.
- Fix a runtime error checking the dependency graph schema using the published
  package.

## 0.31.0

### BREAKING CHANGES

- Require Python 3.9+
- To create DependencyGraph from a class, use `DependencyGraph.from_class()`
  instead of `DependencyGraph()`

### New features

- Add mypy types.
- Add `DependencyGraph.deserialize()`
- Extract Store superclass from StateManager

## 0.30.2

- Fix compatibility with updated semver dependency.

## 0.30.1

Same as 0.30.0.

## 0.30.0

- Upgrade semver dependency.

## 0.29.1

- ComputeGraph: Fix Python 3.9 without typing_extensions, again

## 0.29.0

- When creating new lambdas, default the runtime to the currently running Python
  major and minor version
- ComputeGraph: Fix Python 3.9 without typing_extensions
- Test in Python 3.9

## 0.28.0

- Replace `werkit.aws_lambda.build.find_site_packages_dir()` with
  `site_packages_for_venv()` and fix for Python 3.9+
- Improve RdsDestination debugging
- Update semver dependency to 3.0.0.dev4

## 0.27.0

- ComputeGraph: Rename `coerce()` to `normalize()`
- StateManager: Pass intermediates using normalized values
- Bump boto3 dependency to 1.20.32 to match the AWS Lambda preinstalled
  version
- Bump artifax dependency to 0.5.

## 0.26.0

- StateManager: Serialize no longer triggers evaluation.

## 0.25.1

- StateManager: Prevent exception when invoking `evaluate()` with an empty list.

## 0.25.0

Same as 0.24.0.

## 0.24.0

- Bump artifax dependency to 0.4.

## 0.23.1

- Capitalization fix for previous.

## 0.23.0

- Add compute graph functionality in `werkit.compute.graph`.

## 0.22.0

- Updates for AWS Lambda state functionality.
  - After deploying, wait until function is active.
  - After updating code, wait until function is updated
  - Background:
    https://aws.amazon.com/de/blogs/compute/coming-soon-expansion-of-aws-lambda-states-to-all-functions/
- Sync pinned boto3 to 1.18.55, the version which is preinstalled on AWS
  Lambda.
- Upgrade jsonschema dependency.

## 0.21.1

Same as 0.21.0.

## 0.21.0

### BREAKING CHANGES

- Manager: Add required schema checking
- Adopt new terminology: request -> input_message, serialized_result -> output_message
- Update orchestrator->worker interface to support werkit JSON format
  - Adopt werkit manager in orchestrator lambda
  - Add explicit return schemas
  - Move orchestrator code from `werkit.aws_lambda` to `werkit.orchestrator`

### New features

- Manager: Add optional queue destination

## 0.20.0

### New features

- `publish_to_s3`: Support semver prerelease versions.

## 0.19.1

### Bug fixes

Fix bug in `publish_to_s3` CLI

## 0.19.0

### New features

- Added `publish_to_s3`

### BREAKING CHANGES

Remove `install_werkit` flag from `create_venv_with_dependencies`

## 0.18.0

### BREAKING CHANGES

- Remove `werkit.__version__`.

### New features

- Add `aws_lambda.build.export_poetry_requirements()`.

## 0.17.0

### New features

- `create_venv_with_dependencies`: Optionally omit transitive dependencies.

## 0.16.0

Same as 0.15.0.

## 0.15.0

### BREAKING CHANGES

- Manager: Require that callers set `manager.result` in the context handler as
  intended, returning a compute error if not. To get the old behavior, set
  `manager.result = None`.
- Manager: Extract `note_compute_success()` and `note_compute_exception()` to
  allow more flexibility by consumers.

## 0.14.0

### BREAKING CHANGES

- Lambda deploy functions (e.g. `perform_create()`) require an explicit
  `aws_region`.

## Bug fixes

- Update orchestrator build to support Python 3.8 in addition to 3.7.

## 0.13.0

### BREAKING CHANGES

- For `werkit.aws_lambda.deploy.perform_create()` and `perform_update_code()`,
  the `path_to_zipfile` argument is renamed to `local_path_to_zipfile`. These
  functions can also accept an `s3_path_to_zipfile` which has already been
  uploaded to the `s3_code_bucket`.

## 0.12.0

- Added `force_upload_to_s3_code_bucket` option to Lambda deploy functions
  to force code to be uploaded to S3.

## 0.11.0

- Add `werkit.s3.temp_file_on_s3_from_string()`.
- Document Lambda-building functions.
- Support installing Lambda-building dependencies using
  `pip install werkit[aws_lambda_build]`.

## 0.10.0

### New features

- Manager: Include compute start time and user-provided runtime info

### Other changes

- Update boto dependency.

## 0.9.1

### Bug fixes

- When building Lambda functions, install werkit from PyPI, not GitHub.

## 0.9.0

### Breaking changes

- Generalize `temp_file_on_s3` and move it to `werkit.s3`.
- Provide additional timing metrics.

### New features

- Add CLI command to update-code.

### Other changes

- Replace custom random string code with `uuid.uuid4()`.
- Consolidate duplicate code.

## 0.8.0

### New features

- Optimize the orchestrator using ThreadPoolExecutor.
- Use the same version of werkit in the builder (and don't refer to a
  nonexistent branch).

## 0.7.0

### BREAKING CHANGES

- Adopt consistent schema for compute and orchestration errors.
- Validate that cloud results match the schema.
- By default, do not install dependencies for the Lambda client. When these
  dependencies are desired, use `pip install werkit[client]`.

### New features

- Add `error_source` key to cloud results, which can be `"compute"`,
  `"system"` or `"orchestration"`.
- `werkit.parallel`: Optionally augment result with Lambda roundtrip time.
- By default, provide compute times rounded to the nearest 1/100 of a second.

### Bug fixes

- Fix Lambda update when code is under 50 MB.
- `Manager`: In verbose mode, print timing to stderr instead of stdout.

### Other changes

- Document the cloud result schema.
- Update aioboto3 dependency.

## 0.6.0

### New features

- Support fanout on AWS Lambda, using a werkit orchestrator with a
  user-provided worker lambda.
- Add utilities for deploying Python-based functions to AWS Lambda.

## 0.5.0

### New features

- CloudManager: Allow passing extra args to `docker build`.
- CloudManager: Add `build()` method.

## 0.4.0

### BREAKING CHANGES

- Require Python 3.
- Require RQ 1.2.0+ (not yet released).

### New features

- Remove failed jobs before expiration

### Bug fixes

- Fix stack trace printing.

## 0.3.3

- Make Redis and rq soft depenencies.

## 0.3.2

- Make Redis URL optional when it is not needed.

## 0.3.1

- Fix Redis URL configuration.

## 0.3.0

- Add support for distributed jobs using Redis, RQ, and the Fargate CLI.

## 0.2.0

- Propagate KeyboardInterupt and SystemExit exceptions.

## 0.1.0

Initial release
