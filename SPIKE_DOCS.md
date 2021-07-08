## Demonstration

Once the Terraform has been applied, there will be a Storage Gateway with an NFS file share, and a Datasync task that will move data from the file share to a separate S3 bucket.

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
dd if=/dev/urandom bs=1024 count=1024 >demo-file;
```
