resource "aws_security_group" "test_pracmig_ec2_to_storage_sg" {
  name        = "test-pracmig-ec2-to-storage-sg"
  description = "Security group for the datasync agent"
  vpc_id      = aws_vpc.main.id


  ingress {
    description      = "Activation traffic from web browser"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["86.169.113.163/32"]
    //ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
  }
}