#!/bin/bash

DIR=_build/agent_activator
rm -rf "${DIR}/"

pipenv run pip install -r <(PIPENV_VERBOSITY=-1 pipenv lock -r) --target "${DIR}/"
cp -R src/lambdas/agent_activator "${DIR}"

sam package \
  --template src/templates/source-supplier.yml \
  --s3-bucket activation-key-fetcher \
  --output-template-file src/templates/packaged-source-supplier.yml