resource "aws_storagegateway_gateway" "supplier_simulation_file_gateway" {
  gateway_ip_address = aws_instance.storage_gateway_instance.private_ip
  gateway_name       = "supplier_simulation_file_gateway"
  gateway_timezone   = "GMT"
  gateway_type       = "FILE_S3"
}

resource "aws_storagegateway_nfs_file_share" "supplier_nfs_file_share" {
  client_list  = [aws_subnet.supplier_simulation_subnet.cidr_block]
  gateway_arn  = aws_storagegateway_gateway.supplier_simulation_file_gateway.arn
  location_arn = aws_s3_bucket.supplier_bucket.arn
  role_arn     = aws_iam_role.storage_gateway_role.arn
}