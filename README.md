# Simple Email Service

This project is an experiment of how to build servless web-service with modern tools and frameworks. Main purpose is to make overview of available instruments and find advantages and disadvantages of this approach. As payload this service also can send emails via some emails providers. [Mailgun](http://www.mailgun.com/) and [SparkPost](https://www.sparkpost.com/) are currently supported.  

## Getting Started

Despite of cloud and servless oriented of this service you can still develop it locally

### Prerequisites

To run tests locally you need to provide DB_URL and DB_PASSWORD environment variables 

```
DB_URL=postgresql://postgres:{password}@localhost:5432/postgres
DB_PASSWORD=pass
```

`{password}` will be replaced with DB_PASSWORD

If don't have locally installed PostgreSQL instance you can use Docker to get it with one command:

```
docker run --name some-postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres 
```

When you get connection to DB you should create db schema. You can execute SQL scripts from sql folder one by one or execute apply_db_migration from apps/eservice/emailservice.py

### Installing

All dependencies are presented in requirements.txt. If you use IntelliJ IDEA or PyCharm as IDE they can install them for you. Otherwise you can use pip:

```
pip3 install -r requirements.txt
```

## Running the tests

Pytest is used for tests. You can run tests with:

```
$ DB_URL='postgresql://postgres:{password}@localhost:5432/postgres' DB_PASSWORD=pass python3 -m pytest ./tests/
```

## Deployment

Deployment separated on 2 part:
  * Prepare infrastructure (DBs, VPCs, NATs, SGs and etc) with [Terraform](https://www.terraform.io/)
  * Deploy service with [Servless](https://serverless.com/)
  
### Terraform

Terraform will create AWS infrastructure for service. In your account will be created dedicated VPC with public and private subnet. In private subnet will be created t2.small instance with Postgress. Security group allows traffic to Postgress and HTTPS. 

To prepare infrastructure with Terraform you should create S3 bucket (default: `tfstate-nikita`) where to store state, create DynamoDB table (Default: `TF-Main-LockTable`) for locks and provide credentials to terrafrom (for example you can create file `terraform/stage/eservice/.terraform/credentials.txt` with default credentials).

To create infrastructure execute commands at terraform/stage/eservice:

```
terraform init
terraform apply
```

### Servless

Servless is responsible for integration of AWS ApiGateway and service Lamda function. Also it helps with integration with CloudWatch Logs.

To deploy service with servless you need to create `application-{stack}.yml` (where stack is required stack: dev, stage, prod and etc.) with next params:
* `sg-id` - lambda security group id (output of terraform apply)
* `subnet-ids` - lambda subnets (output of terraform apply) 
* `connection-string` - connection string to EService DB. It will be available at DB_URL env
* `mailgun-api-key`, `mailgun-api-url`, `mailgun-api-from` - API Key, API URL and From_email with verified domain of mailgun provider respectively 
* `sparkpost-api-key`, `sparkpost-api-from`, `sparkpost-api-is-sandbox` - API Key, API From_email with verified domain and use or not sandbox of sparkpost provider respectively
   
To deploy stack use:

```
sls deploy --stack {stack}
```

Where `{stack}` - stack name. Currently only stage
  
## Built With

* [Python3](https://www.python.org/download/releases/3.0/) - The main programming language
* [SqlAlchemy](https://www.sqlalchemy.org/) - The Python SQL Toolkit and Object Relational Mapper
* [lambdarest](https://rometools.github.io/rome/) - Python routing mini-framework for AWS Lambda
* [Terraform](https://www.terraform.io/) - Infrastructure as code framework
* [Serverless](https://serverless.com/) - CLI for building and deploying serverless applications

## Acknowledgments

Python, Terraform and Servless allow to feel whole power of AWS cloud provider at the fingers tips. You can get reliable, robust, securited, edge-optimized web-service for good price with just some extra lines of code.    

However there are some disadvantages:

* There are border between Terraform and Servless. When you use both this frameworks you should connect them by hands or with extra scripts
* Modern web-service is not only API. It is also different daemons or worker which process data or do some other staff and this is convenient way to implement them with Lambda, however Servless don't support multiple lambdas in project. This is possible to deploy lambdas with Terraform, but this is not so convenient as with Servless 

## TODO

* Disable provider if it is not configured. Now miss configuration breaks whole service
* Separate current lambda to lambda with API and lambda with developer operation (db_migration for example) and develop extra terraform scripts  
* Answer the question: will send-query improve robust. if yes add it 
* Add more tests
