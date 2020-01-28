variable "region" {
  default = "us-east-1"
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "terraform_remote_backend_state" {
  # Globally unique s3 bucket name
  bucket = "dev-terraform-basics-in28minutes-001" # Use hyphens as bucket name cannot contain underscores
  
  lifecycle {
    # Safeguard against accidental deletion!
    prevent_destroy = true
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

terraform {
  backend "s3" {
    bucket = "dev-terraform-basics-in28minutes-001"
    key = "global/state-backend/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "dev_terraform_basics_in28minutes_locks"
    encrypt = "true"
  }
}