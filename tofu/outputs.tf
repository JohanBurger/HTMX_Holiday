output "aws_ecr_repo_url" {
  value = aws_ecr_repository.container_repository.repository_url
}

output "aws_ecr_repo_arn" {
  value = aws_ecr_repository.container_repository.arn
}
