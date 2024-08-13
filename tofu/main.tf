terraform {
  backend "s3" {
    bucket = "tofu-state-johan"
    key    = "holidays/tofu.tfstate"
    region = "eu-central-1"
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.62"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_resourcegroups_group" "holidays-resource-group" {
  name        = "holidays-resource-group"
  resource_query {
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [{
        Key    = "Project"
        Values = ["Holidays"]
      }]
    })
  }
}

resource "aws_ecr_repository" "holidays-container-repository" {
  name                 = "holidays-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Project = "Holidays"
  }
}