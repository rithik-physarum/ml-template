output "docker_image_digest" {
  value = data.docker_registry_image.docker_image_digest.sha256_digest
}

output "gcloud_image_info" {
  value = data.google_container_registry_image.docker_image_digest
}


