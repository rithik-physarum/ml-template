locals {
  is_gcr_image = length(regexall(".*gcr\\.io.*", var.docker_image_name)) > 0
  is_artifactory_image = length(regexall(".*.pkg.dev.*", var.docker_image_name)) > 0
}

provider "docker" {
  host        = "https://registry.dci.bt.com"
  // host           = "npipe:////.//pipe//docker_engine"
  registry_auth {
    address     = "europe-west2-docker.pkg.dev"
    config_file = pathexpand("/home/docker_info/config.json")
  }
}

data "docker_registry_image" "docker_image" {
  name = var.docker_image_name
}

data "docker_registry_image" "docker_image_digest" {
  name   = var.docker_image_name
}

data "google_container_registry_image" "docker_image_digest" {
  count = local.is_gcr_image ? 1 : 0

  name   = var.docker_image_name
  digest  = data.docker_registry_image.docker_image_digest.sha256_digest
}

// data "google_artifact_registry_repository" "artifactory_image" {
//   count = local.is_artifactory_image ? 1 : 0

//   name   = var.docker_image_name
//   // digest  = data.docker_registry_image.docker_image_digest.sha256_digest
// }
