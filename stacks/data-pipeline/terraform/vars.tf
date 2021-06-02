variable "environment" {
  type        = string
  description = "Uniquely identities each deployment, i.e. dev, prod."
}

variable "team" {
  type        = string
  default     = "Practice Migration"
  description = "Team owning this resource"
}

variable "repo_name" {
  type        = string
  default     = "prm-practice-migration-data-pipeline-prototype"
  description = "Name of this repository"
}