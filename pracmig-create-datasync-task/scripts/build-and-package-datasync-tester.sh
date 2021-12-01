#!/bin/bash

DIR=_build/datasync_tester
rm -rf "${DIR}/"

pipenv run pip install -r <(PIPENV_VERBOSITY=-1 pipenv lock -r) --target "${DIR}/"
cp -R src/lambdas/datasync_tester "${DIR}"

sam package \
  --template src/templates/datasync-tester.yml \
  --s3-bucket pracmig-datasync-tester \
  --output-template-file src/templates/packaged-datasync-tester.yml