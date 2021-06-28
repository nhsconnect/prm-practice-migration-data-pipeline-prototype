resource "aws_instance" "ec2_instance" {
  ami = "ami-0826a7cca7cf05f06"
  instance_type = "m5.2xlarge"
  tags = {
    Name="EC2_Instance_Terraform"
  }
}