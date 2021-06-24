provider "aws" {
  region  = "eu-west-2"

  default_tags {
      tags = {
        CreatedBy   = var.repo_name
        Environment = var.environment
        Team        = var.team
      }
  }
}