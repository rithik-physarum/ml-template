# Auto Scaling Target
resource "aws_appautoscaling_target" "auto_scaling_target" {
  max_capacity       = local.autoscaling_config.max_replicas
  min_capacity       = local.autoscaling_config.min_replicas
  resource_id        = "service/${local.aws_infra_config.deployment_cluster_name}/${local.project_config.experiment_name}-svc-${local.aws_infra_config.deployment_env}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Step Scaling Policy for Scale Down
resource "aws_appautoscaling_policy" "mem_scale_down" {
  name               = "${local.project_config.experiment_name}-mem-sd-${local.aws_infra_config.deployment_env}"
  resource_id        = aws_appautoscaling_target.auto_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.auto_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.auto_scaling_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = local.autoscaling_config.scale_down_utilization
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }
}

# Step Scaling Policy for Scale Up
resource "aws_appautoscaling_policy" "mem_scale_up" {
  name               = "${local.project_config.experiment_name}-mem-sup-${local.aws_infra_config.deployment_env}"
  resource_id        = aws_appautoscaling_target.auto_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.auto_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.auto_scaling_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = local.autoscaling_config.scale_up_utilization
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 1
      scaling_adjustment          = 1
    }
  }
}

# CloudWatch Alarm for Scale Down
resource "aws_cloudwatch_metric_alarm" "scale_down" {
  alarm_name          = "${local.project_config.experiment_name}-as-sd-${local.aws_infra_config.deployment_env}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  alarm_actions       = [aws_appautoscaling_policy.mem_scale_down.arn]
  alarm_description   = "Scale down alarm for ${local.project_config.experiment_name}"
  datapoints_to_alarm = 1
  dimensions = {
    ClusterName = local.aws_infra_config.deployment_cluster_name
    ServiceName = "${local.project_config.experiment_name}-service"
  }
  metric_name = "CPUUtilization"
  namespace   = "AWS/ECS"
  period      = local.autoscaling_config.scale_down_monitor_period
  statistic   = "Average"
  threshold   = local.autoscaling_config.scale_down_utilization
}

# CloudWatch Alarm for Scale Up
resource "aws_cloudwatch_metric_alarm" "scale_up" {
  alarm_name          = "${local.project_config.experiment_name}-as-sup-${local.aws_infra_config.deployment_env}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  alarm_actions       = [aws_appautoscaling_policy.mem_scale_up.arn]
  alarm_description   = "Scale up alarm for ${local.project_config.experiment_name}"
  datapoints_to_alarm = 1
  dimensions = {
    ClusterName = local.aws_infra_config.deployment_cluster_name
    ServiceName = "${local.project_config.experiment_name}-service"
  }
  metric_name = "CPUUtilization"
  namespace   = "AWS/ECS"
  period      = local.autoscaling_config.scale_up_monitor_period
  statistic   = "Average"
  threshold   = local.autoscaling_config.scale_up_utilization
}
