resource "aws_s3_bucket" "datasync_bucket" {
  bucket = "test-pracmig-datasync-bucket"
  acl    = "private"
}
