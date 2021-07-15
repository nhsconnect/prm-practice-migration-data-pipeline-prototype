# prm-practice-migration-data-pipeline-prototype

Providing a centralised cloud based mechanism in which practice migration data transfers can be done electronically.

## Setup

These instructions assume you are using:

- [dojo](https://github.com/kudulab/dojo) to provide an execution environment
- [assume-role](https://github.com/remind101/assume-role) to set your AWS Credentials

## Applying terraform

To run the terraform locally, run the following commands:

1. Set your AWS Credentials
   ```
   assume-role <profile-name>
   ```
1. Invoke terraform locally

   ```
     ./tasks tf_plan create
     ./tasks tf_apply
   ```
