resource "aws_security_group" "storage_gateway_sg" {
  name        = "storage_gateway_sg"
  description = "Security group for the file storage gateway"
  vpc_id      = aws_vpc.supplier_simulation_vpc.id

  egress {
    description      = "Allow all egress traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}