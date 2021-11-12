#!/bin/bash

DIR=_build

pipenv run pip install -r <(PIPENV_VERBOSITY=-1 pipenv lock -r) --target _build/
cp -R src/* _build

sam package \
  --template source-supplier.yml \
  --s3-bucket activation-key-fetcher \
  --output-template-file packaged-source-supplier.yml