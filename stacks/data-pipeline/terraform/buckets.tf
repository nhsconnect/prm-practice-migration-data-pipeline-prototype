resource "aws_s3_bucket" "datasync_cloud_bucket" {
  bucket = "test-pracmig-datasync-bucket"
  acl    = "private"
}

resource "aws_s3_bucket" "supplier_bucket" {
  bucket = "test-pracmig-supplier-bucket"
  acl    = "private"
}
