variable "environment" {
  default = "default"
}

variable "region" {
  default = "us-east-1"
}

locals {
  extn = "terraform-module-01-001"
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "my_s3_bucket" {
  # Globally unique s3 bucket name
  # bucket = "${var.environment}-terraform-module-01-001" # Use hyphens as bucket name cannot contain underscores  
  bucket = "${var.environment}-${local.extn}" # Use hyphens as bucket name cannot contain underscores  
}

output "module_output" {
  value = aws_s3_bucket.my_s3_bucket.arn
}