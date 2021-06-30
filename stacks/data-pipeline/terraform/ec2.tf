resource "aws_instance" "datasync_agent" {
  ami = "ami-0826a7cca7cf05f06"
  instance_type = "m5.2xlarge"
  subnet_id = "${aws_subnet.main.id}"
  vpc_security_group_ids = [aws_security_group.test_pracmig_ec2_to_storage_sg.id]

  tags = {
    Name="EC2_Instance_Terraform"
  }
}
