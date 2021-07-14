# Declare the data source
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_availability_zone" "az" {
  name = data.aws_availability_zones.available.names[0]
}
