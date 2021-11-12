#!/bin/bash

while getopts o:a:n:p:b: flag
do
    case "${flag}" in
        o) OdsCode=${OPTARG};;
        a) DataSyncAgentArn=${OPTARG};;
        n) SourceNfsServer=${OPTARG};;
        p) SourceNfsPath=${OPTARG};;
        b) TargetS3BucketArn=${OPTARG};;
    esac
done

aws cloudformation create-stack \
  --template-body "$(cat ./datasync.yml)"\
  --timeout-in-minutes 30 \
  --stack-name "datasync-migration-$OdsCode" \
  --parameters ParameterKey=OdsCode,ParameterValue=$OdsCode\
               ParameterKey=DataSyncAgentArn,ParameterValue=$DataSyncAgentArn\
               ParameterKey=SourceNfsServer,ParameterValue=$SourceNfsServer\
               ParameterKey=SourceNfsPath,ParameterValue=$SourceNfsPath\
               ParameterKey=TargetS3BucketArn,ParameterValue=$TargetS3BucketArn\
  --disable-rollback \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM