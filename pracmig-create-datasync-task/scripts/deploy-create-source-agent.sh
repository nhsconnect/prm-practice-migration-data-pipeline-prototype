#!/bin/bash
# Helper for creating the source agent stack

while getopts c:i:k: flag
do
    case "${flag}" in
        c) CidrBlockAllowedAccessToBastion="${OPTARG}";;
        i) id="${OPTARG}";;
        k) BastionKeyName="${OPTARG}";;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./src/templates/packaged-source-supplier.yml)" \
  --parameters ParameterKey=CidrBlockAllowedAccessToBastion,ParameterValue="${CidrBlockAllowedAccessToBastion}" \
               ParameterKey=BastionKeyName,ParameterValue="${BastionKeyName}" \
  --timeout-in-minutes 30 \
  --stack-name "source-supplier-${id}" \
  --disable-rollback \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM