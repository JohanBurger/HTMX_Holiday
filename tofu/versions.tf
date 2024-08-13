terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.62"
    }
  }

  backend "s3" {
    bucket = "tofu-state-johan"
    key    = "holidays/tofu.tfstate"
    region = "eu-central-1"
  }
}