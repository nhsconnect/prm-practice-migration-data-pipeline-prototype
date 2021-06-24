# prm-practice-migration-data-pipeline-prototype
Providing a centralised cloud based mechanism in which practice migration data transfers can be done electronically.

## Setup

These instructions assume you are using:

- [dojo](https://github.com/kudulab/dojo) to provide an execution environment
- [assume-role](https://github.com/remind101/assume-role) to set your AWS Credentials

## Applying terraform

Rolling out terraform against each environment is managed by the GoCD pipeline. If you'd like to test it locally, run the following commands:

1. Set your AWS Credentials

`assume-role <profile-name>`

2. Enter the container

`dojo`

3. Invoke terraform locally

```
  ./tasks validate <stack-name> <environment>
  ./tasks plan <stack-name> <environment>
```

The stack name denotes the specific stack you would like to validate.
The environment can be `dev` or `preprod`.

To run the formatting, run `./tasks format <stack-name> <environment>`
