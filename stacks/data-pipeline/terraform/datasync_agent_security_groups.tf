resource "aws_security_group" "datasync_agent_sg" {
  name        = "datasync_agent_sg"
  description = "Security group for the datasync agent"
  vpc_id      = aws_vpc.supplier_simulation_vpc.id

  # ingress {
  #   description      = "Activation traffic from web browser"
  #   from_port        = 80
  #   to_port          = 80
  #   protocol         = "tcp"
  #   cidr_blocks      = ["86.169.113.163/32"]
  # }

  egress {
    description      = "Allow all egress traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  # egress {
  #   description = "Activation traffic for agent"
  #   from_port = 443
  #   to_port = 443
  #   protocol = "TCP"
  #   cidr_blocks = ["activation.datasync.eu-west-2.amazonaws.com/32"]
  # }

  # egress {
  #   description = "Communication traffic for agent"
  #   from_port = 443
  #   to_port = 443
  #   protocol = "TCP"
  #   cidr_blocks = ["activation.datasync.eu-west-2.amazonaws.com"]
  # }
}