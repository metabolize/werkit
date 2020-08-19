# Changelog

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
