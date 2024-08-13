provider "aws" {
  region = "eu-central-1"
}

resource "aws_resourcegroups_group" "resource_group" {
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

resource "aws_ecr_repository" "container_repository" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Project = "Holidays"
  }
}