resource "aws_instance" "storage_gateway_instance" {
  ami = "ami-018c255c04483b4a2"
  instance_type = "m5.xlarge"
  subnet_id = "${aws_subnet.suppiler_simulation_subnet.id}"
  vpc_security_group_ids = [aws_security_group.storage_gateway_sg.id]

  tags = {
    Name = "Storage gateway"
  }
}
