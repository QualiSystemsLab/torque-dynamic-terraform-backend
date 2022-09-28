data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "torque-terraform-backend-network"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "compute" {
  backend = "s3"
  config = {
    bucket = "torque-terraform-backend-compute"
    key    = "compute/terraform.tfstate"
    region = "us-west-2"
  }
}

data "aws_ami" "example" {
  most_recent = true

  owners = ["self"]
  tags = {
    Name   = "app-server"
    Tested = "true"
  }
}