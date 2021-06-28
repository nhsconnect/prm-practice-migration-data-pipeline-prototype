data "aws_region" "current" {}

resource "aws_vpc_endpoint" "pracmig" {
  service_name       = "com.amazonaws.${data.aws_region.current.name}.datasync"
  vpc_id             = aws_vpc.main.id
//  security_group_ids = [aws_security_group.example.id]
  subnet_ids         = [aws_subnet.main.id]
  vpc_endpoint_type  = "Interface"
}
