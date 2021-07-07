Setup Steps:
- Create a client that mounts NFS, with granted permissions
  - mount command:
`mount -t nfs -o nolock,hard [Storage Gateway IP]:/test-pracmig-supplier-bucket [MountPath]`
- Moved client into the same subnet as Storage Gateway
- Updated the Security Gateway

