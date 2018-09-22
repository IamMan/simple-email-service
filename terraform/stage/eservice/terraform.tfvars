allowed_cidr_blocks = [
  "0.0.0.0/0"
]

tags                = {
  Terraform   = "true"
  Owner       = "nikita"
  Environment = "stage"
  Stack       = "dbs"
}

env                 = "stage"
env_upper           = "Stage"

vpc_name = "nikita-stage-vpc"
vpc_cidr_block     = "10.20.0.0/16"

availability_zones = ["eu-west-1a", "eu-west-1b"]
private_subnets    = ["10.20.50.0/24", "10.20.51.0/24"]
public_subnets     = ["10.20.0.0/24", "10.20.1.0/24"]
