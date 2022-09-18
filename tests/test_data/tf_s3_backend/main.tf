terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">3.0.0"
    }
  }

  backend "s3" {
    bucket = "my-bucket"
    key    = "path/to/my/key"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.region
}

data "aws_iam_user" "input_user" {
  user_name = "my_user"
}

resource "aws_s3_bucket" "bucket" {
  bucket = "my-bucket"
  force_destroy = true

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
