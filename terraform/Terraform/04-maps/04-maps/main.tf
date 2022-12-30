variable "names" {
  default = ["ravs","sats","ranga", "tom","jane"]
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_user" "my_iam_users" {
  # count = length(var.names)
  # name  = var.names[count.index]
  for_each = toset(var.names)
  name = each.value
}