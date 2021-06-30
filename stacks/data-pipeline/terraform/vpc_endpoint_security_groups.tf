resource "aws_security_group" "test_pracmig_vpc_endpoint_to_storage_sg" {
  name        = "test-pracmig-vpc-endpoint-to-storage-sg"
  description = "Security group for the VPC endpoint"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "TLS from VPC"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["${aws_instance.datasync_agent.private_ip}/32"]
    //ipv6_cidr_blocks = [aws_instance.datasync_agent.private_ip]
  }

  ingress {
    description      = "TLS from VPC"
    from_port        = 1024
    to_port          = 1064
    protocol         = "tcp"
    cidr_blocks      = ["${aws_instance.datasync_agent.private_ip}/32"]
    //ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
  }

//  egress {
//    from_port        = 0
//    to_port          = 0
//    protocol         = "-1"
//    cidr_blocks      = ["0.0.0.0/0"]
//    //ipv6_cidr_blocks = ["::/0"]
//  }

  tags = {
    Name = "allow_tls"
  }
}