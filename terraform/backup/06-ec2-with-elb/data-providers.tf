data "aws_subnet" "default_subnet_1" {
  filter {
    name   = "availability-zone"
    values = ["us-east-1d"]
  }
}

data "aws_subnet" "default_subnet_2" {
  filter {
    name   = "availability-zone"
    values = ["us-east-1a"]
  }
}

data "aws_ami" "aws_linux_2_latest" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}
