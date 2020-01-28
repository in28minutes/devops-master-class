module "first_module"{
	source = "../../modules/first-module"
	environment = "qa" #CHANGE
}

output "module_output" {
  value = module.first_module.module_output
}

terraform {
  backend "s3" {
    bucket = "dev-terraform-basics-in28minutes-001"
    key = "qa/s3/terraform.tfstate" #CHANGE
    region = "us-east-1"
    dynamodb_table = "dev_terraform_basics_in28minutes_locks"
    encrypt = "true"
  }
}