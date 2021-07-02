resource "aws_vpc" "datasync_agent_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "datasync agent VPC"
  }
}

resource "aws_subnet" "suppiler_simulation_subnet" {
  vpc_id     = aws_vpc.datasync_agent_vpc.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "Datasync agent subnet"
  }
}
