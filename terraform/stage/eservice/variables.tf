variable "tags" {
  type = "map"
}

variable "allowed_cidr_blocks" {
  type = "list"
}

variable "env" {}
variable "env_upper" {}

variable "private_subnets" {
  type = "list"
}

variable "public_subnets" {
  type = "list"
}

variable "availability_zones" {
  type = "list"
}

variable "vpc_cidr_block" {}

variable "vpc_name" {}