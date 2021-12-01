#!/bin/bash
# Helper for creating the target supplier S3 bucket

while getopts n: flag
do
    case "${flag}" in
        n) bucket_name="${OPTARG}";;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./src/templates/target-supplier.yml)" \
  --stack-name "target-supplier-${bucket_name}" \
  --disable-rollback \
  --parameters ParameterKey=BucketName,ParameterValue="${bucket_name}"
