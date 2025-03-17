variable region {
  type        = string
  description = "(Required) The region for resourcs"
  default = "eu-west-2"
}

variable "ecs_image_uri" {
  type = string
  description = "(Required) Uri of the image to be used in the ECS service."
}

variable "env" {
  type = string
  description = "(Required) Deployment Environment."
}
