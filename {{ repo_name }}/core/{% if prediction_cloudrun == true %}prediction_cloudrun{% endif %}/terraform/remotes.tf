data "terraform_remote_state" "base_networking" {
  backend = "gcs"
  config = {
    bucket = var.networking_remote_state_bucket
    prefix = var.networking_remote_state_prefix
  }
}
