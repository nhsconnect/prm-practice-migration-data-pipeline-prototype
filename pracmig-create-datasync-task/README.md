## Create DataSync Task Lambda

### Prerequisites

- [pyenv](https://github.com/pyenv/pyenv#installation)
- Python 3.8.12 (installed with `pyenv`)
- `pipenv`: `pip install pipenv`
- Install dependencies: `pipenv install --dev`
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- An [EC2 key-pair in AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)

### Running the tests

To run the tests from the CLI, first ensure your virtual environment is activated, e.g. with `pipenv shell`, and then run `pytest`.

### Deploy

#### Creating a mock DataSync Agent

Build and package the activator lambda:

```shell
./scripts/build-and-package-source-agent.sh
```

Deploy the mock datasync agent stack:

```shell
./scripts/deploy-create-source-agent.sh -i <YOUR_UNIQUE_ID> -k <EC2_KEY_PAIR_NAME>
```

#### Registering a DataSync Agent

Deploy the register agent stack:

```shell
./scripts/deploy-register-agent.sh -o <ODS_CODE> -a <DATASYNC_AGENT_ACTIVATION_KEY>
```

#### Creating a mock target supplier bucket

Deploy the target supplier stack:

```shell
./scripts/deploy-target-supplier-infra.sh -n <BUCKET_NAME>
```

#### Create a DataSync task

Deploy the datasync task stack

```shell
./scripts/deploy-datasync-task.sh \
    -o <ODS_CODE> \
    -a <DATASYNC_AGENT_ARN> \
    -n <SourceNfsServer> \
    -p <SourceNfsPath> \
    -b <TargetS3BucketArn>
```

#### Deploy the DataSync tester lambda

Build and package the datasync tester lambda:

```shell
./scripts/build-and-package-datasync-tester.sh
```

Deploy the datasync tester lambda:

```shell
./scripts/deploy-datasync-tester.sh \
    -n '<SUBNET_OF_NFS_SERVER>' \
    -g '<SECURITY_GROUP_OF_NFS_SERVER>' \
    -i <YOUR_UNIQUE_ID>
```
