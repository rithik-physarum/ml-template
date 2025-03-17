locals {
  project_config  = yamldecode(file("${path.module}/../../config/${var.env}/project_config.yaml"))
  prediction_config  = yamldecode(file("${path.module}/../../config/${var.env}/prediction_aws_config.yaml"))
  aws_infra_config = local.prediction_config.aws_infra_config
  autoscaling_config = local.aws_infra_config.autoscaling_config
  security_group_config = local.aws_infra_config.security_group_config
  iam_config = local.aws_infra_config.iam_config
}

data "aws_vpc" "dev_vpc" {
  id = local.aws_infra_config.vpc_id
}

data "aws_ecs_cluster" "nba_cluster" {
  cluster_name = local.aws_infra_config.deployment_cluster_name
}

data "aws_iam_role" "ecsTaskExecutionRole" {
  name = local.iam_config.execution_role
}

data "aws_iam_role" "ecsTaskRole" {
  name = local.iam_config.task_role
}

resource "aws_cloudwatch_log_group" "log-group" {
  name = "${local.project_config.experiment_name}-${local.aws_infra_config.deployment_env}"

  tags = {
    Application = "${local.project_config.experiment_name}-${local.aws_infra_config.deployment_env}"
  }
}

resource "aws_ecs_task_definition" "ecs_task_defination" {
  family                   = "${local.project_config.experiment_name}-task-${local.aws_infra_config.deployment_env}"
  cpu                      = local.aws_infra_config.cpu
  memory                   = local.aws_infra_config.memory
  execution_role_arn       = "${data.aws_iam_role.ecsTaskExecutionRole.arn}"
  task_role_arn            = "${data.aws_iam_role.ecsTaskRole.arn}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  container_definitions = jsonencode([
    {
      name      = "${local.project_config.experiment_name}-task-${local.aws_infra_config.deployment_env}"
      image     = var.ecs_image_uri
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.log-group.name
          awslogs-region        = var.region
          awslogs-stream-prefix = local.project_config.experiment_name
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "curl -f http://localhost:${local.aws_infra_config.port}/live || exit 1"
        ]
        interval     = 60
        timeout      = 10
        retries      = 9
        startPeriod  = 10
      }

      portMappings = [
        {
          containerPort = local.aws_infra_config.port
          hostPort      = local.aws_infra_config.port
        }
      ]

      memory = local.aws_infra_config.memory
      cpu    = local.aws_infra_config.cpu
    }
  ])
}

resource "aws_security_group" "security_group" {
  name        = "${local.project_config.experiment_name}-sg-${local.aws_infra_config.deployment_env}"
  description = "Security group with combined rules"
  vpc_id      = local.aws_infra_config.vpc_id

  dynamic "egress" {
    for_each = flatten([for subnet, rules in local.security_group_config.egress_rules : rules])
    content {
      cidr_blocks = egress.value.cidr_blocks
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = "tcp"
    }
  }

  dynamic "ingress" {
    for_each = flatten([for subnet, rules in local.security_group_config.ingress_rules : rules])
    content {
      cidr_blocks = ingress.value.cidr_blocks
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = "tcp"
    }
  }
}

resource "aws_ecs_service" "ecs_service" {
  name            = "${local.project_config.experiment_name}-svc-${local.aws_infra_config.deployment_env}"
  cluster         = "${data.aws_ecs_cluster.nba_cluster.id}"
  task_definition = "${aws_ecs_task_definition.ecs_task_defination.arn}"
  launch_type     = local.aws_infra_config.launch_type
  desired_count   = local.autoscaling_config.desired_count

  network_configuration {
    subnets = local.aws_infra_config.subnet_list
    assign_public_ip = false
    security_groups = [aws_security_group.security_group.id]
  }


  service_registries {
    registry_arn = "${aws_service_discovery_service.service-discovery.arn}"
  }

  depends_on = [
    aws_service_discovery_service.service-discovery
  ]

}
