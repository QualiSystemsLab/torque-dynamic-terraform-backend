terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">3.0.0"
    }
  }

  backend "wtf" {
    bucket = "my-bucket"
    key    = "path/to/my/key"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.region
}
