resource "aws_instance" "datasync_agent" {
  ami = "ami-0826a7cca7cf05f06"
  instance_type = "m5.2xlarge"
  subnet_id = "${aws_subnet.suppiler_simulation_subnet.id}"
  vpc_security_group_ids = [aws_security_group.datasync_agent_sg.id]

  tags = {
    Name="Datasync agent"
  }
}
