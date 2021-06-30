resource "aws_datasync_task" "pracmig_datasync_task" {
  destination_location_arn = aws_datasync_location_s3.destination_location.arn
  name                     = "pracmig"
  source_location_arn      = aws_datasync_location_s3.source_location.arn
}

resource "aws_datasync_location_s3" "source_location" {
  s3_bucket_arn = aws_s3_bucket.datasync_bucket.arn
  subdirectory  = "/source"

  s3_config {
    bucket_access_role_arn = aws_iam_role.datasync_bucket_access_role.arn
  }
}

resource "aws_datasync_location_s3" "destination_location" {
  s3_bucket_arn = aws_s3_bucket.datasync_bucket.arn
  subdirectory  = "/destination"

  s3_config {
    bucket_access_role_arn = aws_iam_role.datasync_bucket_access_role.arn
  }
}