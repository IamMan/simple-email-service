provider "aws" {
  region                  = "eu-west-1"
}

terraform {
  backend "s3" {
    encrypt                 = true
    bucket                  = "tfstate-nikita"
    key                     = "stage/eservice"
    region                  = "eu-west-1"
    dynamodb_table          = "TF-Main-LockTable"
  }
}

