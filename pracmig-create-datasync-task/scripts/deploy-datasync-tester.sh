#!/bin/bash
# Helper for creating the datasync tester stack

while getopts i:v:n: flag
do
    case "${flag}" in
        i) id="${OPTARG}";;
        n) DeploymentSubnetId="${OPTARG}";;
        v) DeploymentVpcId="${OPTARG}";;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./src/templates/packaged-datasync-tester.yml)" \
  --parameters ParameterKey=DeploymentSubnetId,ParameterValue="${DeploymentSubnetId}" \
               ParameterKey=DeploymentVpcId,ParameterValue="${DeploymentVpcId}" \
  --timeout-in-minutes 30 \
  --stack-name "datasync-tester-${id}" \
  --capabilities CAPABILITY_NAMED_IAM
