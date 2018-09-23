data "aws_ssm_parameter" "stage_eservice_db_admin_pass" {
  name = "/nikita/terraform/${var.env}/project/eservice/rds/admin_pass"
}


module "stage_eservice_db" {
  source                    = "terraform-aws-modules/rds/aws"
  identifier                = "${var.env}-eservice-db"
  availability_zone         = "${local.default_az}"
  engine                    = "postgres"
  engine_version            = "9.6.6"
  instance_class            = "db.t2.small"
  allocated_storage         = 50
  storage_encrypted         = false
  publicly_accessible       = false
  apply_immediately         = true
  name                      = "eservicedb"

  username                  = "eservice_db_admin"
  password                  = "${data.aws_ssm_parameter.stage_eservice_db_admin_pass.value}"
  port                      = "5432"

  vpc_security_group_ids    = ["${module.stage_eservice_security_group.this_security_group_id}"]

  # disable backups to create DB faster
  backup_retention_period   = 1

  # DB subnet group
  subnet_ids                = ["${module.vpc.private_subnets}"]

  # DB parameter group
  family                    = "postgres9.6"

  # Snapshot name upon DB deletion
  final_snapshot_identifier = "${var.env}-eservice-db"
  skip_final_snapshot       = false

  maintenance_window        = "Mon:00:00-Mon:03:00"
  backup_window             = "03:00-06:00"

  tags                      = "${var.tags}"
  parameters                = [{
    name         = "rds.force_ssl"
    value        = 1
    apply_method = "pending-reboot"
  }]
}

module "stage_eservice_security_group" {
  source                   = "terraform-aws-modules/security-group/aws"
  version                  = "2.5.0"
  name                     = "stage-eservice-rds-sg"
  vpc_id                   = "${module.vpc.vpc_id}"

  egress_ipv6_cidr_blocks  = []
  ingress_with_cidr_blocks = [
    {
      rule        = "postgresql-tcp"
      cidr_blocks = "${join(",", var.allowed_cidr_blocks)}"
    },
    {
      rule        = "https-443-tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      rule        = "https-443-tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  ingress_with_self        = [{
    from_port = 5432,
    to_port   = 5432,
    protocol  = "TCP"
  }]
  egress_with_self         = [{
    from_port = 5432,
    to_port   = 5432,
    protocol  = "TCP"
  }]
  tags                     = "${var.tags}"
}

output "stage_eservice_db_address" {
  value = "${module.stage_eservice_db.this_db_instance_address}"
}

output "stage_eservice_db_name" {
  value = "${module.stage_eservice_db.this_db_instance_name}"
}

output "stage_eservice_sg" {
  value = "${module.vpc.default_vpc_default_security_group_id}"
}

output "stage_eservice_private_subnets" {
  value = "${module.vpc.private_subnets}"
}