# variables.tf
variable "db_password" {
  description = "Password for MariaDB root user"
  type        = string
  sensitive   = true  # This marks the variable as sensitive in logs
}

variable "key_name" {
  description = "Name of the AWS key pair to use for SSH access"
  type        = string
}