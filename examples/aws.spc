# AWS plugin configuration example.
# Mount this file to: /home/steampipe/.steampipe/config/aws.spc
#
# Credentials are read from environment variables (recommended for containers):
#   AWS_ACCESS_KEY_ID
#   AWS_SECRET_ACCESS_KEY
#   AWS_DEFAULT_REGION
#
# Or from a mounted ~/.aws/credentials file.

connection "aws" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
}

# Multi-account setup with an aggregator:
#
# connection "aws_dev" {
#   plugin  = "aws"
#   profile = "dev"
#   regions = ["us-east-1"]
# }
#
# connection "aws_prod" {
#   plugin  = "aws"
#   profile = "prod"
#   regions = ["us-east-1", "eu-west-1"]
# }
#
# connection "aws_all" {
#   plugin      = "aws"
#   type        = "aggregator"
#   connections = ["aws_dev", "aws_prod"]
# }
