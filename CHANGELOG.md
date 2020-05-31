# Changelog

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
