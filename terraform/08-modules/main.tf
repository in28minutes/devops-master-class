provider "aws" {
    region = "us-east-1"
    //version = "~> 2.46" (No longer necessary)
}

resource "aws_iam_user" "my_iam_user" {
    name = "my_iam_user_abc_updated"
}