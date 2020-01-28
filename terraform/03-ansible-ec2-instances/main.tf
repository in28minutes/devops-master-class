variable "aws_key_pair" {
  default = "~/aws/aws_keys/default-ec2.pem"
}

variable "region" {
  default = "us-east-1"
}

variable "aws_hardcoded_subnets" {
  default = ["subnet-3ebdf810", "subnet-23efdf2c"]
}

provider "aws" {
  region = var.region
}

resource "aws_default_vpc" "default" {
}

resource "aws_security_group" "http_servers_sg" {
  name   = "http_servers_sg"
  vpc_id = aws_default_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # add a CIDR block here
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # add a CIDR block here
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"] # add a CIDR block here
  }

}

data "aws_ami" "aws-linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}

data "aws_subnet_ids" "subnets" {
  vpc_id = aws_default_vpc.default.id
}

resource "aws_instance" "http_servers" {
  count                  = length(var.aws_hardcoded_subnets)
  ami                    = data.aws_ami.aws-linux.id
  key_name               = "default-ec2"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.http_servers_sg.id]
  subnet_id              = var.aws_hardcoded_subnets[count.index]
  tags = {
    type = "http"
    env  = "production"
  }
}

#tolist
output "aws_instance_public_dns" {
  value = aws_instance.http_servers
}