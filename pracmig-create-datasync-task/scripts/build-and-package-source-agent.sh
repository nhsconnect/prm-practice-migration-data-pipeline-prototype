#!/bin/bash

DIR=_build
rm -rf "${DIR}/"

pipenv run pip install -r <(PIPENV_VERBOSITY=-1 pipenv lock -r) --target "${DIR}/"
cp -R src/lambdas/* "${DIR}"

sam package \
  --template src/templates/source-supplier.yml \
  --s3-bucket activation-key-fetcher \
  --output-template-file src/templates/packaged-source-supplier.yml