# prm-practice-migration-data-pipeline-prototype

Providing a centralised cloud based mechanism in which practice migration data transfers can be done electronically.

## Setup

These instructions assume you are using:

- [dojo](https://github.com/kudulab/dojo) to provide an execution environment
- [assume-role](https://github.com/remind101/assume-role) to set your AWS Credentials

## Applying terraform

To run the terraform locally, run the following commands:

1. Set your AWS Credentials
   ```bash
   eval $(assume-role ci)
   ```
2. Set the NHS environment variables and target region
   ```bash
   export NHS_ENVIRONMENT=test
   export NHS_SERVICE=practice-migration
   export AWS_DEFAULT_REGION=eu-west-2
   ```
3. Invoke terraform locally
   ```bash
   ./tasks tf_plan create
   ./tasks tf_apply
   ```

## End-to-end test lambda

To test a deployed data transfer setup, there is a lambda that can be invoked locally or deployed and run using the [serverless framework](serverless.com).

### Prerequisites

#### Python

A python 3 environment is required; it is recommended to set up a virtual environment. To do this, run the following commands in the `/test/e2e/` directory.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install dependencies into the environment
pip install -r requirements.txt
```

In subsequent sessions, you will only need to run the `source` command from the same directory that the virtual environment was created in:

```bash
source venv/bin/activate
```

#### AWS

The lambda works by writing a file to a "source bucket", triggering a DataSync Task, and then reading the (hopefully!) transferred file from the "target bucket". In order for this to work, it needs to run with an IAM role that has permission to:

1. Write to the source bucket.
1. Execute the DataSync task that is specified as an argument.
1. Assume the target-bucket-access-role that is specified as an argument.

This also means that such a target-bucket-access-role must exist (something to bear in mind if testing a DataSync task that transfers files to a target bucket in an account outside of the practice migration team's control).

### Running locally

To invoke the lambda locally, first set your AWS credentials in the terminal (bearing in mind the prerequisites, above):

```bash
eval $(assume-role ci)
```

Once your python environment is setup, the lambda can be invoked locally by running:

```bash
npx sls invoke local --function testMigrator --data '{"TaskArn": "arn:aws:datasync:eu-west-2:<task-account-id>:task/task-<task-id>", "TargetBucketAccessRoleArn": "arn:aws:iam::<target-bucket-account-id>:role/<target-role-name>"}'
```

from the `test/e2e/testDataMigrator/` directory (replace the account IDs, task ID and role name with the appropriate values).
