variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "youtube-job"
}

variable "ecr_repository_name" {
  type    = string
  default = "youtube-job"
}

variable "image_tag" {
  type        = string
  description = "Docker image tag in ECR (e.g., git SHA)."
}

variable "youtube_api_key" {
  type        = string
  description = "YouTube API key (we'll move this to Secrets Manager later)."
  sensitive   = true
}

variable "schedule_expression" {
  type        = string
  description = "EventBridge schedule expression."
  default     = "rate(1 day)"
}

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}