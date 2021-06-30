resource "aws_iam_role" "datasync_bucket_access_role" {
  name = "datasync_bucket_access_role"
  managed_policy_arns = [aws_iam_policy.datasync_storage_access_policy.arn]

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "datasync.amazonaws.com"
        }
      },
    ]
  })

}

resource "aws_iam_policy" "datasync_storage_access_policy" {
  name = "datasync_storage_access_policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        Action: [
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads"
        ],
        Effect: "Allow",
        Resource: aws_s3_bucket.datasync_bucket.arn
      },
      {
        Action: [
          "s3:AbortMultipartUpload",
          "s3:DeleteObject",
          "s3:GetObject",
          "s3:ListMultipartUploadParts",
          "s3:PutObjectTagging",
          "s3:GetObjectTagging",
          "s3:PutObject"
        ],
        Effect: "Allow",
        Resource: "${aws_s3_bucket.datasync_bucket.arn}/*"
      }
    ]
  })
}

