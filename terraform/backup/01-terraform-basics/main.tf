provider "aws" {
    region = "us-east-1"
    //version = "~> 2.46" (No longer necessary)
}

# plan - execute 
resource "aws_s3_bucket" "my_s3_bucket" {
    bucket = "my-s3-bucket-in28minutes-rangak-002"
 #   versioning {
 #       enabled = true
 #   }
}

resource "aws_s3_bucket_versioning" "versioning_example" {
  bucket = aws_s3_bucket.my_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}


resource "aws_iam_user" "my_iam_user" {
    name = "my_iam_user_abc_updated"
}