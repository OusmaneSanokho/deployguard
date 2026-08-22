terraform {
  backend "s3" {
    bucket       = "deployguard-tfstate-ousmane-2989"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
