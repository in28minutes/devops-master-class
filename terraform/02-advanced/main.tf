variable "key_name" {
  default = "default-ec2"
}

variable "aws_key_pair" {
  default = "~/aws/aws_keys/default-ec2.pem"
}

variable "region" {
  default = "us-east-1"
}

provider "aws" {
  region = var.region
}

variable "vpc_cidr" {
	default = "10.20.0.0/16"
}

variable "subnets_cidr" {
	type = list(string)
	default = ["10.20.1.0/24", "10.20.2.0/24"]
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "aws-linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }
}

# CREATE RESOURCES
# create VPC - AWS Networking #
resource "aws_vpc" "tf_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = "true"
  tags = {
    Name = "AWS_Terraform_VPC"
  }
  
}
resource "aws_internet_gateway" "terraform_igw" {
  vpc_id = aws_vpc.tf_vpc.id

  tags = {
    Name = "AWS_Terraform_IGW"
  }
}

resource "aws_subnet" "tf_subnets" {
  count                   = 2
  cidr_block              = var.subnets_cidr[count.index]
  vpc_id                  = aws_vpc.tf_vpc.id
  map_public_ip_on_launch = "true"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "AWS_Terraform_Subnet"
  }
}

# ROUTING #
resource "aws_route_table" "tf_rtb" {
  vpc_id = aws_vpc.tf_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.terraform_igw.id
  }

  tags = {
    Name = "AWS_Terraform_RouteTable"
  }
}

resource "aws_route_table_association" "rta-subnets" {
  count = 2
  subnet_id      = aws_subnet.tf_subnets[count.index].id
  route_table_id = aws_route_table.tf_rtb.id
}

# SECURITY GROUPS #
resource "aws_security_group" "elb-sg" {
  name   = "webserver_elb_sg"
  vpc_id = aws_vpc.tf_vpc.id

  #Allow HTTP from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# create apache webserver security group 
resource "aws_security_group" "webserver-sg" {
  name   = "webserver_sg"
  vpc_id = aws_vpc.tf_vpc.id

  # SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from the VPC
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# LOAD BALANCER #
resource "aws_elb" "elb" {
  name = "webserver-elb"

  subnets         = aws_subnet.tf_subnets.*.id
  security_groups = [aws_security_group.elb-sg.id]
  instances       = aws_instance.webservers.*.id

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
}

resource "aws_instance" "webservers" {
  count = 2
  ami                    = data.aws_ami.aws-linux.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.tf_subnets[count.index].id
  vpc_security_group_ids = [aws_security_group.webserver-sg.id]
  key_name               = var.key_name

  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ec2-user"
    private_key = file(var.aws_key_pair)

  }

 provisioner "remote-exec" { # NOT A GOOD PRACTICE 
    inline = [
      "sudo yum install httpd -y",
      "sudo service httpd start",
      "echo ${self.public_dns} | sudo tee /var/www/html/index.html"
    ]

  }
}

output "aws_elb_public_dns" {
  value = aws_elb.web.dns_name
}