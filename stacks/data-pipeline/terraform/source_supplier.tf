resource "aws_s3_bucket" "source_supplier_bucket" {
  bucket = "test-pracmig-source-supplier-bucket"
  acl    = "private"
}

resource "aws_instance" "source_supplier" {
  ami = "ami-03ac5a9b225e99b02"
  instance_type = "t2.micro"
  subnet_id = "${aws_subnet.source_supplier_subnet.id}"
  vpc_security_group_ids = [aws_security_group.source_supplier_instance_sg.id]
  key_name = "pracmig"
  availability_zone = data.aws_availability_zone.az.name

  tags = {
    Name="Source supplier instance"
  }
}

resource "aws_security_group" "source_supplier_instance_sg" {
  name        = "source_supplier_instance_sg"
  description = "Security group for the EC2 instance"
  vpc_id      = aws_vpc.source_supplier_vpc.id

  ingress {
    description      = "Allow SSH ingress access for Emily"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["86.169.113.163/32"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description      = "Allow all egress traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_instance" "source_supplier_datasync_agent" {
  ami = "ami-0826a7cca7cf05f06"
  instance_type = "m5.2xlarge"
  subnet_id = "${aws_subnet.source_supplier_subnet.id}"
  vpc_security_group_ids = [aws_security_group.source_supplier_datasync_agent_sg.id]

  tags = {
    Name="Source supplier datasync agent"
  }
}

resource "aws_security_group" "source_supplier_datasync_agent_sg" {
  name        = "source_supplier_datasync_agent_sg"
  description = "Security group for the datasync agent"
  vpc_id      = aws_vpc.source_supplier_vpc.id

  ingress {
    description      = "Allow http ingress access for Emily"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["86.169.113.163/32"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description      = "Allow all egress traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_iam_role" "source_supplier_datasync_bucket_access_role" {
  name = "source_supplier_datasync_bucket_access_role"
  managed_policy_arns = [aws_iam_policy.source_datasync_storage_access_policy.arn]

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "datasync.amazonaws.com"
        }
      },
    ]
  })

}

resource "aws_iam_policy" "source_datasync_storage_access_policy" {
  name = "source_datasync_storage_access_policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        Action: [
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads"
        ],
        Effect: "Allow",
        Resource: aws_s3_bucket.datasync_cloud_bucket.arn
      },
      {
        Action: [
          "s3:AbortMultipartUpload",
          "s3:DeleteObject",
          "s3:GetObject",
          "s3:ListMultipartUploadParts",
          "s3:PutObjectTagging",
          "s3:GetObjectTagging",
          "s3:PutObject"
        ],
        Effect: "Allow",
        Resource: "${aws_s3_bucket.datasync_cloud_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_storagegateway_gateway" "source_supplier_storage_gateway" {
  gateway_ip_address = aws_instance.source_supplier_storage_gateway_instance.public_ip
  gateway_name       = "source_supplier_storage_gateway"
  gateway_timezone   = "GMT"
  gateway_type       = "FILE_S3"
}

resource "aws_storagegateway_nfs_file_share" "source_supplier_nfs_file_share" {
  client_list  = [aws_subnet.source_supplier_subnet.cidr_block]
  gateway_arn  = aws_storagegateway_gateway.source_supplier_storage_gateway.arn
  location_arn = aws_s3_bucket.source_supplier_bucket.arn
  role_arn     = aws_iam_role.source_supplier_storage_gateway_role.arn
}

resource "aws_volume_attachment" "source_ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.source_supplier_storage_gateway_volume.id
  instance_id = aws_instance.source_supplier_storage_gateway_instance.id
}

resource "aws_ebs_volume" "source_supplier_storage_gateway_volume" {
  availability_zone = aws_instance.source_supplier_storage_gateway_instance.availability_zone
  size              = 150
}

data "aws_storagegateway_local_disk" "source_supplier_storage_gateway_local_disk" {
  disk_node   = "/dev/sdh"
  gateway_arn = aws_storagegateway_gateway.source_supplier_storage_gateway.arn
}

resource "aws_storagegateway_cache" "source_supplier_storage_gateway_cache" {
  disk_id     = data.aws_storagegateway_local_disk.source_supplier_storage_gateway_local_disk.id
  gateway_arn = aws_storagegateway_gateway.source_supplier_storage_gateway.arn
}

resource "aws_instance" "source_supplier_storage_gateway_instance" {
  ami = "ami-018c255c04483b4a2"
  instance_type = "m5.xlarge"
  subnet_id = "${aws_subnet.source_supplier_subnet.id}"
  vpc_security_group_ids = [aws_security_group.source_supplier_storage_gateway_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "Source supplier storage gateway"
  }
}

resource "aws_iam_role" "source_supplier_storage_gateway_role" {
  name = "source_supplier_storage_gateway_role"
  managed_policy_arns = [aws_iam_policy.source_datasync_storage_access_policy.arn]

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "storagegateway.amazonaws.com"
        }
      },
    ]
  })

}

resource "aws_security_group" "source_supplier_storage_gateway_sg" {
  name        = "source_supplier_storage_gateway_sg"
  description = "Security group for the file storage gateway"
  vpc_id      = aws_vpc.source_supplier_vpc.id

  ingress {
    description      = "Allow http ingress access for Emily"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["86.169.113.163/32"]
  }

  ingress {
    description      = "Allow storage gateway traffic"
    from_port        = 2049
    to_port          = 2049
    protocol         = "tcp"
    cidr_blocks      = [aws_subnet.source_supplier_subnet.cidr_block]
  }

  ingress {
    description      = "Allow storage gateway traffic"
    from_port        = 111
    to_port          = 111
    protocol         = "tcp"
    cidr_blocks      = [aws_subnet.source_supplier_subnet.cidr_block]
  }

  ingress {
    description      = "Allow storage gateway traffic"
    from_port        = 20048
    to_port          = 20048
    protocol         = "tcp"
    cidr_blocks      = [aws_subnet.source_supplier_subnet.cidr_block]
  }

  egress {
    description      = "Allow all egress traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_vpc" "source_supplier_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "Source supplier VPC"
  }
}

resource "aws_subnet" "source_supplier_subnet" {
  vpc_id     = aws_vpc.source_supplier_vpc.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone = data.aws_availability_zone.az.name

  tags = {
      Name = "Source supplier subnet"
    }
}

resource "aws_internet_gateway" "source_supplier_internet_gateway" {
  vpc_id = aws_vpc.source_supplier_vpc.id

  tags = {
    Name = "Source supplier internet gateway"
  }
}


resource "aws_default_route_table" "source_supplier_route_table" {
  default_route_table_id = aws_vpc.source_supplier_vpc.default_route_table_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.source_supplier_internet_gateway.id
  }

  tags = {
    Name = "Source supplier route table"
  }
}