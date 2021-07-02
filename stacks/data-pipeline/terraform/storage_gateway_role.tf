resource "aws_iam_role" "storage_gateway_role" {
  name = "storage_gateway_role"
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
          Service = "storagegateway.amazonaws.com"
        }
      },
    ]
  })

}