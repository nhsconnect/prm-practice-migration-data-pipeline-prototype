#!/bin/bash
# Helper for registering a datasync agent

while getopts o:a: flag
do
    case "${flag}" in
        o) ods=${OPTARG};;
        a) key=${OPTARG};;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./register-datasync-agent.yml)" \
  --capabilities CAPABILITY_NAMED_IAM \
  --timeout-in-minutes 30 \
  --stack-name "register-datasync-agent-${ods}" \
  --disable-rollback \
  --parameters ParameterKey=OdsCode,ParameterValue="${ods}" \
               ParameterKey=DataSyncAgentActivationKey,ParameterValue="${key}"