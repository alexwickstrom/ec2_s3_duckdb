variable "private_key" {
  type    = string
  default = "/Users/alex/.ssh/mtc_dev_key" # update with your own
}


variable "db_username" {
  description = "The username for the database"
  default     = "myuser"
}

variable "db_password" {
  description = "The password for the database"
  default     = "mypassword"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.small" # small instance
}
