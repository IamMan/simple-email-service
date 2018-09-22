locals {
  env_tags   = "${var.tags}"
  default_az = "${var.availability_zones[0]}"
}
resource "aws_eip" "nat_eip" {
  count = 1
  vpc   = true
}
data "aws_region" "current" {}

module "vpc" {
  source                       = "terraform-aws-modules/vpc/aws"
  version                      = "1.30.0"


  enable_nat_gateway           = true
  single_nat_gateway           = true
  reuse_nat_ips                = true

  external_nat_ip_ids          = ["${aws_eip.nat_eip.id}"]

  name                         = "${var.vpc_name}"
  private_subnets              = "${var.private_subnets}"
  public_subnets               = "${var.public_subnets}"
  cidr                         = "${var.vpc_cidr_block}"
  azs                          = "${var.availability_zones}"

  create_database_subnet_group = false
  enable_dns_hostnames         = true

  enable_s3_endpoint           = true
  tags                         = "${local.env_tags}"
}

