# CloudWatch Alarms for Arbor Energy Plan Agent
# Apply with: terraform apply

variable "sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  default     = "production"
}

# API Response Time Alarm
resource "aws_cloudwatch_metric_alarm" "api_response_time" {
  alarm_name          = "arbor-${var.environment}-api-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 2  # 2 seconds target
  alarm_description   = "API response time exceeds 2 second target"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = "app/arbor-${var.environment}-alb/xxx"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# High Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "arbor-${var.environment}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High 5xx error rate detected"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = "app/arbor-${var.environment}-alb/xxx"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "arbor-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization above 80%"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    ClusterName = "arbor-cluster"
    ServiceName = "arbor-${var.environment}"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Memory Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "arbor-${var.environment}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS memory utilization above 80%"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    ClusterName = "arbor-cluster"
    ServiceName = "arbor-${var.environment}"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Database Connection Alarm
resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "arbor-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS connections above 80%"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = "arbor-${var.environment}-db"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Redis Cache Memory Alarm
resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "arbor-${var.environment}-redis-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "ElastiCache memory usage above 75%"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    CacheClusterId = "arbor-${var.environment}-redis"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Health Check Failure Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_failures" {
  alarm_name          = "arbor-${var.environment}-health-failures"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Minimum"
  threshold           = 1
  alarm_description   = "No healthy targets available"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    TargetGroup  = "targetgroup/arbor-${var.environment}-tg/xxx"
    LoadBalancer = "app/arbor-${var.environment}-alb/xxx"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Request Count Spike Alarm (for DDoS/abuse detection)
resource "aws_cloudwatch_metric_alarm" "request_spike" {
  alarm_name          = "arbor-${var.environment}-request-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RequestCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10000  # Adjust based on normal traffic
  alarm_description   = "Unusual spike in request volume"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    LoadBalancer = "app/arbor-${var.environment}-alb/xxx"
  }

  tags = {
    Environment = var.environment
    Application = "arbor-energy-agent"
  }
}

# Output alarm ARNs
output "alarm_arns" {
  description = "ARNs of created CloudWatch alarms"
  value = {
    api_response_time    = aws_cloudwatch_metric_alarm.api_response_time.arn
    high_error_rate      = aws_cloudwatch_metric_alarm.high_error_rate.arn
    high_cpu             = aws_cloudwatch_metric_alarm.high_cpu.arn
    high_memory          = aws_cloudwatch_metric_alarm.high_memory.arn
    database_connections = aws_cloudwatch_metric_alarm.database_connections.arn
    redis_memory         = aws_cloudwatch_metric_alarm.redis_memory.arn
    health_check         = aws_cloudwatch_metric_alarm.health_check_failures.arn
    request_spike        = aws_cloudwatch_metric_alarm.request_spike.arn
  }
}
