## Activation

Activation requires the terraform host to have a rout to port 80 for the activation target. In this spike both of the EC2 activation targets are on a private subnet with no Internet Gateway so as a work around both the DataSync agent and the Storage Gateway can be activiated via the AWS console.

#### StorageGateway  

1. Visit the StorageGateway in AWS console
2. Under the Gateways tab choose "Create Gateway"
3. Follow instructions to activate the EC2 gateway

#### DataSync

1. Visit the DataSync in AWS console
2. Under the Agents tab choose "Add Agent"
3. Follow instructions to activate the EC2 agent.

## Demonstration

Once the Terraform has been applied, there will be a Storage Gateway with an NFS file share, and a DataSync task that will move data from the file share to a separate S3 bucket.

To demonstrate it working, there needs to be a way to put files into the file share. This can be done by starting a simple EC2 instance that mounts the file share.

### Adding a file to the file share using an EC2 client

1. Start an EC2 instance, ensuring that it has permission to connect to the file share (for example, by putting it in the same subnet as the Storage Gateway). This can be a simple t2.micro-sized linux instance.
1. Mount the file share:

   ```
   mount -t nfs -o nolock,hard [Storage Gateway IP]:/test-pracmig-supplier-bucket /mnt/demo
   ```

1. Add files to the mounted directory.

   - A random, 1MB file can be generated using the following command:

     ```
     dd if=/dev/urandom bs=1024 count=1024 >/mnt/demo/demo-file;
     ```

### Executing the DataSync task

To execute the DataSync task, which will transfer any files in the file share to the destination bucket, go to the [Tasks section](https://eu-west-2.console.aws.amazon.com/datasync/home?region=eu-west-2#/tasks) of the AWS Console, select the task, and click the _Start_ button (choose _Start with defaults_).

### Checking the destination bucket

Once the DataSync task has completed, open the [destination S3 bucket](https://s3.console.aws.amazon.com/s3/buckets/test-pracmig-datasync-bucket?region=eu-west-2&tab=objects#) in the AWS Console. In it, there should be a _destination_ directory containing a copy of each file in the file share.

