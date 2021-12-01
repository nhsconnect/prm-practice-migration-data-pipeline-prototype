#!/bin/bash
# Helper for creating the datasync tester stack

while getopts i:g:n: flag
do
    case "${flag}" in
        i) id="${OPTARG}";;
        g) DeploymentSecurityGroupId="${OPTARG}";;
        n) DeploymentSubnetId="${OPTARG}";;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./src/templates/packaged-datasync-tester.yml)" \
  --parameters ParameterKey=DeploymentSubnetId,ParameterValue="${DeploymentSubnetId}" \
               ParameterKey=DeploymentSecurityGroupId,ParameterValue="${DeploymentSecurityGroupId}" \
  --timeout-in-minutes 30 \
  --stack-name "datasync-tester-${id}" \
  --capabilities CAPABILITY_NAMED_IAM
