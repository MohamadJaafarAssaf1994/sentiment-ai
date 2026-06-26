variable "image_tag" {
  description = "Tag de l'image Docker a deployer"
  type        = string
  default     = "latest"
}

variable "app_port" {
  description = "Port expose en staging"
  type        = number
  default     = 8001
}

variable "container_name" {
  description = "Nom du conteneur staging"
  type        = string
  default     = "sentiment-staging"
}

variable "registry" {
  description = "Registry Docker"
  type        = string
  default     = "ghcr.io/mohamadjaafarassaf1994"
}

variable "docker_host" {
  description = "Docker host used by Terraform"
  type        = string
  default     = "npipe:////./pipe/docker_engine"
}
