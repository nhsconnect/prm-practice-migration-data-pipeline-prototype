#!/bin/bash
# Helper for creating the source agent stack

while getopts i:c: flag
do
    case "${flag}" in
        c) CidrBlockAllowedAccessToBastion=${OPTARG};;
        i) id=${OPTARG};;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./packaged-source-supplier.yml)" \
  --parameters ParameterKey=CidrBlockAllowedAccessToBastion,ParameterValue=$CidrBlockAllowedAccessToBastion \
  --timeout-in-minutes 30 \
  --stack-name "source-supplier-$id" \
  --disable-rollback \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM