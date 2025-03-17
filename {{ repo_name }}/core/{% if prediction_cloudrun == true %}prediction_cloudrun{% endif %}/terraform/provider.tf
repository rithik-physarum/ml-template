provider "google" {
  version = "~> 4.29.0"

  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  version = "~> 4.29.0"

  project = var.project_id
  region  = var.region
}
