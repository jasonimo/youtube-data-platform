provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# Use default VPC to keep this simple
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# --- ECR ---
resource "aws_ecr_repository" "repo" {
  name = var.ecr_repository_name
}

# --- CloudWatch Logs ---
resource "aws_cloudwatch_log_group" "lg" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 14
}

# --- IAM: Task Execution Role (pull image, write logs) ---
data "aws_iam_policy_document" "ecs_task_execution_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_execution_role" {
  name               = "${var.project_name}-task-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume.json
}

resource "aws_iam_role_policy_attachment" "task_exec_attach" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn  = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "cluster" {
  name = "${var.project_name}-cluster"
}

# --- Security group for task (egress only) ---
resource "aws_security_group" "task_sg" {
  name        = "${var.project_name}-sg"
  description = "Egress-only SG for Fargate task"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- ECS Task Definition ---
locals {
  image_uri = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/${aws_ecr_repository.repo.name}:${var.image_tag}"
}

resource "aws_ecs_task_definition" "task" {
  family                   = var.project_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory

  execution_role_arn = aws_iam_role.task_execution_role.arn
  # task_role_arn optional (not needed until your container calls AWS APIs)

  container_definitions = jsonencode([
    {
      name      = var.project_name
      image     = local.image_uri
      essential = true
      environment = [
        { name = "YOUTUBE_API_KEY", value = var.youtube_api_key }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.lg.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# --- IAM role for EventBridge Scheduler to run ECS task ---
data "aws_iam_policy_document" "scheduler_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_role" {
  name               = "${var.project_name}-scheduler"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume.json
}

data "aws_iam_policy_document" "scheduler_policy" {
  statement {
    actions = ["ecs:RunTask"]
    resources = [aws_ecs_task_definition.task.arn]
  }

  statement {
    actions = ["iam:PassRole"]
    resources = [
      aws_iam_role.task_execution_role.arn
    ]
  }
}

resource "aws_iam_role_policy" "scheduler_role_policy" {
  name   = "${var.project_name}-scheduler-policy"
  role   = aws_iam_role.scheduler_role.id
  policy = data.aws_iam_policy_document.scheduler_policy.json
}

# --- EventBridge Scheduler (runs task on schedule) ---
resource "aws_scheduler_schedule" "schedule" {
  name                = "${var.project_name}-schedule"
  schedule_expression = var.schedule_expression

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_ecs_cluster.cluster.arn
    role_arn  = aws_iam_role.scheduler_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.task.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = data.aws_subnets.default.ids
        security_groups  = [aws_security_group.task_sg.id]
        assign_public_ip = true
      }
    }
  }
}