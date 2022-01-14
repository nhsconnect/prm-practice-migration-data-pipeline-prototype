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

The DataSync Task requires source and target locations. Since, in a real deployment, these would be part of the source and target suppliers' infrastructure, we need to create mock ones for the purposes of developing and testing the DataSync Task creation code.

#### Creating a mock DataSync Agent

The source location for the DataSync Task, which is assumed to be an NFS (Network File Storage) file share, will consist of a DataSync Agent, the IP address of the NFS server and the file share path on the NFS server. The scripts for the mock source supplier will create a VPC (representing the source supplier's network) along with 3 EC2 instances - 1 being the NFS server, 1 being the DataSync Agent, and 1 acting as a "bastion", or "jump-box", enabling SSH access into the network. This latter is useful when trying to debug problems.

Build and package the mock source supplier stack:

```shell
./scripts/build-and-package-source-agent.sh
```

Deploy the mock source supplier stack:

```shell
./scripts/deploy-create-source-agent.sh \
    -k '<EC2_KEY_PAIR_NAME>' \
    -c '<CIDR_BLOCK_ALLOWED_ACCESS_TO_BASTION>' \
    -i '<SOME_UNIQUE_ID>'
```

- `EC2_KEY_PAIR_NAME`: a key pair to use for SSH access to the EC2 instances that are created
- `CIDR_BLOCK_ALLOWED_ACCESS_TO_BASTION`: a CIDR block that will be allowed SSH access to the bastion, i.e. your own IP address (if specifying a single IP address, don't forget to add a trailing `/32` to make it a valid CIDR block).
- `SOME_UNIQUE_ID`: a unique ID for this stack (enables deploying the stack multiple times into the same AWS account)

#### Registering a DataSync Agent

This script will register the agent created in the preceding step with the AWS DataSync service.

Deploy the register agent stack:

```shell
./scripts/deploy-register-agent.sh -o '<ODS_CODE>' -a '<DATASYNC_AGENT_ACTIVATION_KEY>'
```

- `ODS_CODE`: a unique string that will be used as part of the DataSync Agent's name to help with differentiating between multiple registered agents
- `DATASYNC_AGENT_ACTIVATION_KEY`: the DataSync Agent's activation key; this can be found as an output of the stack that creates the mock source supplier.

#### Creating a mock target supplier bucket

The target location for the DataSync Task is assumed to be an S3 bucket. The script for the mock target supplier will create that bucket.

Deploy the target supplier stack:

```shell
./scripts/deploy-target-supplier-infra.sh -n '<BUCKET_NAME>'
```

- `BUCKET_NAME`: the name to use for the created bucket.

#### Create a DataSync task

This script creates the DataSync Task, which is the only "real" script (i.e. it could be used for a real deployment).

Deploy the datasync task stack:

```shell
./scripts/deploy-datasync-task.sh \
    -o '<ODS_CODE>' \
    -a '<DATASYNC_AGENT_ARN>' \
    -n '<SOURCE_NFS_HOST>' \
    -p '<SOURCE_NFS_PATH>' \
    -b '<TARGET_S3_ARN>'
```

- `ODS_CODE`: a unique string, used to name some of the created AWS components such that they are easily identifiable as part of a given migration
- `DATASYNC_AGENT_ARN`: The DataSync Agent's ARN; if using the mock source supplier stack, this can be found as an output of the stack that registers the agent
- `SOURCE_NFS_HOST`: the IP address of the source supplier NFS server; if using the mock source supplier stack, this can be found as an output of that stack
- `SOURCE_NFS_PATH`: the file share path on the source supplier NFS server; if using the mock source supplier stack, this can be found inside the `source-supplier.yml` template in the `templates/` directory
- `TARGET_S3_ARN`: the ARN of the target supplier S3 bucket; if using the mock target supplier stack, this can be found as an output of that stack.

#### Deploy the DataSync tester lambda

The DataSync tester lambda can be used to test the DataSync Task (when deployed along with the mock source and target suppliers). It will first write a file to the source supplier NFS file share, then invoke the DataSync Task, and finally, check that the file was transferred to the target supplier S3 bucket. It is designed to be deployed to the mock source supplier VPC and in the same subnet as the NFS server (so it will have network connectivity to it).

Build and package the datasync tester lambda:

```shell
./scripts/build-and-package-datasync-tester.sh
```

Deploy the datasync tester lambda:

```shell
./scripts/deploy-datasync-tester.sh \
    -n '<SUBNET_ID_OF_NFS_SERVER>' \
    -v '<VPC_ID_OF_NFS_SERVER>' \
    -i '<SOME_UNIQUE_ID>'
```

- `SUBNET_ID_OF_NFS_SERVER`: the ID of the subnet that the NFS server from the mock source supplier stack resides in
- `VPC_ID_OF_NFS_SERVER`: the ID of the VPC that the NFS server from the mock source supplier stack resides in
- `SOME_UNIQUE_ID`: a unique ID for this stack (enables deploying the stack multiple times into the same AWS account; does not need to match the unique ID used for creating the mock source supplier stack)

Invoke the datasync tester lambda:

```shell
aws lambda invoke \
    --function-name '<DATASYNC_TESTER_LAMBDA_NAME>' \
    --invocation-type Event \
    --payload '{ "TaskArn": "<DATASYNC_TASK_ARN>" }' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

- `DATASYNC_TESTER_LAMBDA_NAME`: the resource name of the lambda; can be found as an output of the DataSync tester lambda stack
- `DATASYNC_TASK_ARN`: the DataSync Task's ARN; can be found as an output of the DataSync Task stack

### Troubleshooting

#### SSH access to EC2 instances in mock source supplier stack

If there are any problems when running the various scripts, it can be useful to be able to SSH onto the EC2 instances, for example, to check network connectivity. The key-pair that is specified when deploying the mock source supplier stack will be set up for all 3 of the instances that it creates, and connections will be allowed to the bastion host from the IP address range that was also specified then.

Connecting to the bastion host is simple, as it can be connected to directly, like so:

```shell
ssh -i '<PATH_TO_PRIVATE_KEY>' ec2-user@<BASTION_PUBLIC_IP>
```

- `PATH_TO_PRIVATE_KEY`: the path on your filesystem to the private SSH key that corresponds to the key-pair that was used when deploying the mock source supplier stack
- `BASTION_PUBLIC_IP`: the public IP address of the bastion host.

However, to connect to the DataSync Agent and NFS server, you cannot simply SSH from the bastion host, as it does not have the private key installed on it. Instead, you can create an SSH tunnel from your local machine through the bastion to the desired target machine.

Set up an SSH tunnel to the DataSync Agent or NFS server:

```shell
ssh -fi '<PATH_TO_PRIVATE_KEY>' -L <LOCAL_PORT>:<PRIVATE_IP>:22 ec2-user@<BASTION_PUBLIC_IP> -N
```

- `PATH_TO_PRIVATE_KEY`: the path on your filesystem to the private SSH key that corresponds to the key-pair that was used when deploying the mock source supplier stack
- `LOCAL_PORT`: any free port on your local machine, for example, 10022
- `PRIVATE_IP`: the private IP address of the target machine you wish to connect to (i.e. the DataSync Agent or NFS server)
- `BASTION_PUBLIC_IP`: the public IP address of the bastion host.

Use the tunnel to connect to the target machine:

```shell
ssh -i '<PATH_TO_PRIVATE_KEY>' <USERNAME>@localhost -p <LOCAL_PORT>
```

- `PATH_TO_PRIVATE_KEY`: the path on your filesystem to the private SSH key that corresponds to the key-pair that was used when deploying the mock source supplier stack
- `USERNAME`: the username, on the target machine, that has the private key associated with it; for the DataSync Agent this will be "admin", and for the NFS server this will be "ec2-user"
- `LOCAL_PORT`: the port that was used when setting up the tunnel, for example, 10022.
