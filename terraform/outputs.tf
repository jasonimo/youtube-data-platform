output "ecr_repository_url" {
  value = aws_ecr_repository.repo.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.cluster.name
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.lg.name
}

output "image_uri" {
  value = "${aws_ecr_repository.repo.repository_url}:${var.image_tag}"
}