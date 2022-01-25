#!/bin/bash
# Helper for creating the source agent stack

while getopts i:k:s:v: flag
do
    case "${flag}" in
        i) id="${OPTARG}";;
        k) SshKeyName="${OPTARG}";;
        s) SubnetId="${OPTARG}";;
        v) SourceSupplierVpcId="${OPTARG}";;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./src/templates/packaged-source-supplier-agent.yml)" \
  --parameters ParameterKey=SubnetId,ParameterValue="${SubnetId}" \
               ParameterKey=SourceSupplierVpcId,ParameterValue="${SourceSupplierVpcId}" \
               ParameterKey=SshKeyName,ParameterValue="${SshKeyName}" \
  --timeout-in-minutes 30 \
  --stack-name "source-supplier-agent-${id}" \
  --disable-rollback \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM