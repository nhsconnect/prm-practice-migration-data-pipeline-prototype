resource "aws_s3_bucket" "source_bucket" {
  bucket = "test-pracmig-datasync-source-bucket"
  acl    = "private"
}