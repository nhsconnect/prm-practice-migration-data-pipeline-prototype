## Status

While performing this spike we discovered that it is not actually possible to set up a DataSync task from one NFS file share to another. Once we discovered this, we stopped working on trying to resolve our Terraform issues, so the Terraform apply does not complete successfully.

## Running the Terraform

If you do decide to run the Terraform, before doing so, all occurrences of the CIDR block "86.169.113.163/32" need replacing with the IP address of the machine that you are running Terraform from.

Once those substitutions have been made, the Terraform can be run as detailed in the README, however it will not completely succeed. An error similar to the following occurs twice, once for the source supplier and once for the target:

```
Error: error waiting for Storage Gateway NFS File Share ("arn:aws:storagegateway:eu-west-2:327778747031:share/share-8956E0FB") to be Available: unexpected state 'UNAVAILABLE', wanted target 'AVAILABLE'. last error: %!s(<nil>)

  with aws_storagegateway_nfs_file_share.source_supplier_nfs_file_share,
  on source_supplier.tf line 139, in resource "aws_storagegateway_nfs_file_share" "source_supplier_nfs_file_share":
 139: resource "aws_storagegateway_nfs_file_share" "source_supplier_nfs_file_share" {
```

Therefore, once the Terraform apply has completed, the file shares that Terraform has created will need to be deleted and recreated using the AWS Console. When doing this, allow AWS to create the IAM role, rather than using the one created by Terraform, as otherwise it does not become available.

No DataSync task will have been created, though since it is not possible to create one with both source and destination being NFS file shares, this doesn't really matter.
