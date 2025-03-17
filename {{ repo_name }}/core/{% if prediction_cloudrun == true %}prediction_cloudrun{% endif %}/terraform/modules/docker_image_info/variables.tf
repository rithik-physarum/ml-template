variable "docker_image_name" {
  type      = string
  default   = ""
}

variable "image_registry" {
  description = "Docker registry"
  type      = string
  default   = ""
}

variable "docker_username" {
  description = "Docker registry username"
  type        = string
  default     = ""
}

variable "docker_password" {
  description = "Docker registry password"
  type        = string
  default     = ""
}

variable "config_file_path" {
  description = "Docker registry config file path"
  type        = string
  default     = ""
}

variable "config_file_content" {
  description = "Docker registry config file content"
  type        = string
  default     = ""
}
