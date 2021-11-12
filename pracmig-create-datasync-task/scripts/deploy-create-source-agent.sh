#!/bin/bash
# Helper for creating the source agent stack

while getopts i: flag
do
    case "${flag}" in
        i) id=${OPTARG};;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./packaged-source-supplier.yml)" \
  --timeout-in-minutes 30 \
  --stack-name "source-supplier-$id" \
  --disable-rollback \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM