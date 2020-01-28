# brew install terraform
# export AWS_ACCESS_KEY_ID=*****
# export AWS_SECRET_ACCESS_KEY=*****
# terraform init
# terraform plan
# terraform apply
# terraform validate
# chmod 400 default-ec2.pem 
# ssh -vvv -i ~/aws/aws_keys/default-ec2.pem ec2-user@34.231.110.243
# mkdir ~/aws/
# mkdir ~/aws/aws_keys
# mv default-ec2.pem ~/aws/aws_keys
# ls ~/aws/aws_keys
# terraform fmt
# terraform destroy
# terraform graph

# variable "NAME" {
# description = "What is this variable used for? You will see this when you do terraform plan or apply without providing a default value. TRY THIS"
# default = "What is the default value?"
# type = any (default), string, number, bool, list, map, set, object, tuple
## Variable REFERENCE = var.<NAME>
## if type does not match default or value, error!! 
## terraform console -var="name=value"
## terraform console -var="only_in_terraform_tfvars=value"
## export TF_VAR_only_in_terraform_tfvars=environment_value
#}

variable "only_in_terraform_tfvars" {

}

variable "aws_key_pair" {
  default = "~/aws/aws_keys/default-ec2.pem"
}

variable "region" {
  default = "us-east-1"
}

variable "list_of_regions" { #var.list_of_regions[0]
  type    = list(string)
  default = ["region-1", "region-2"]
}

variable "map_of_amis" { #var.map_of_amis[var.list_of_regions[0]]
  type = map(string)
  default = {
    "region-1" : "ami-1"
    "region-2" : "ami-2"
  }
}

provider "aws" {
  region = var.region
}



//Use S3 Buckets instead of iam users!
resource "aws_iam_user" "users" {
  count = 2
  name = "user_${count.index}"  
}

variable "names" {
  default = ["ranga", "ravi", "tom"]
}

resource "aws_iam_user" "users_from_names" {
  count = length(var.names)
  name = var.names[count.index]

  # Do not use length! Problems if you remove something from the array!
}

output "users_arn" {
  value = aws_iam_user.users_from_names[*].arn
}

resource "aws_s3_bucket" "s3_buckets_from_names" {
  for_each = toset(var.names)
  bucket = "in28min-s3-bucket-001-${each.value}"
  # You can remove a name and the bucket is deleted!
}

output "s3_arn" {
  value = aws_s3_bucket.s3_buckets_from_names[*]
}

resource "aws_default_vpc" "default" {
  
}

## Changing resource name will cause resource to be recreated
resource "aws_security_group" "http_servers_sg" {
  name   = "http_servers_sg"
  vpc_id = aws_default_vpc.default.id
  
  ## Adding and removing ingress or egress will not recreate the ec2 instances

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
    #cidr_blocks = ["0.0.0.0/0"] # add a CIDR block here
    cidr_blocks = [aws_default_vpc.default.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"] # add a CIDR block here
  }

}


# multi region
# highly secure
# auto updates
data "aws_ami" "aws-linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}


# After creating load balancer, see how the updates happen automatically if we add a new subnet in here!
variable "aws_hardcoded_subnets" {
  default = ["subnet-3ebdf810","subnet-23efdf2c"]
}

#terraform console
#data.aws_subnet_ids.subnets, data.aws_subnet_ids.subnets.ids
#tolist(data.aws_subnet_ids.subnets.ids),tolist(data.aws_subnet_ids.subnets.ids)[0]
data "aws_subnet_ids" "subnets" {
  vpc_id = aws_default_vpc.default.id
}

resource "aws_instance" "http_servers" {
  count                  = length(var.aws_hardcoded_subnets)
  ami                    = data.aws_ami.aws-linux.id
  key_name               = "default-ec2"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.http_servers_sg.id]
  
  subnet_id = var.aws_hardcoded_subnets[count.index]
  #for_each = data.aws_subnet_ids.subnets.ids
  #subnet_id              = each.value

  connection {
    type         = "ssh"
    host         = self.public_ip
    user         = "ec2-user"
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

# SECURITY GROUPS #
resource "aws_security_group" "elb-sg" {
  name   = "elb_sg"
  vpc_id = aws_default_vpc.default.id

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


resource "aws_elb" "elb" {
  name = "elb"

  subnets         = var.aws_hardcoded_subnets
  security_groups = [aws_security_group.elb-sg.id]
  instances       = aws_instance.http_servers.*.id

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
}


#tolist
output "aws_instance_public_dns" {
  #value = aws_instance.http_servers
  value = aws_elb.elb
  #description = ""
  #sensitive=true # Does not log it when you do terraform apply
  #can you have multiple output variables?
}

resource "aws_s3_bucket" "terraform_remote_backend_state" {
  # Globally unique s3 bucket name
  bucket = "dev-terraform-basics-in28minutes-001" # Use hyphens as bucket name cannot contain underscores
  
  lifecycle {
    # Safeguard against accidental deletion!
    # prevent_destroy = true
  }

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_remote_backend_lock" {
  name = "dev_terraform_basics_in28minutes_locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "LockID" # Match spelling and capitalization
  attribute {
    name = "LockID"
    type = "S"
  }
}

# terraform init to reinitialize
terraform {
  ## Example : Workspaces
  ## Example : Workspaces
  ## terraform workspace show
  ## terraform workspace new dev
  ## terraform workspace new qa
  ## terraform workspace select default
  ## terraform workspace list

  backend "s3" {
    bucket = "dev-terraform-basics-in28minutes-001"
    key = "global/s3/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "dev_terraform_basics_in28minutes_locks"
    encrypt = "true"
  }
} 

output "s3_bucket_id" {
  value = aws_s3_bucket.terraform_remote_backend_state.arn
}

output "dynamodb_state_lock_table_name" {
  value = aws_dynamodb_table.terraform_remote_backend_lock.name
}