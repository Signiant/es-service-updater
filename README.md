# es-service-updater

[![Build Status](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda.svg?branch=master)](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda)

# Purpose
Lambda function to send notifications to a specified slack channel every monday at 9am if there is an update available 
for specified open search clusters in the region this is deployed to.

* run ./deploy.sh {s3-bucket} {env} {region} {lambda-prefix} "SlackChannel={channelname} DomainName={elastic domain name} Region={region} SlackWebhookUrl={slackwebhookurl}"

# Installing
The easiest deployment of this solution is using AWS SAM
* export your AWS credentials (or use --profile option with sam commands)
* update the samconfig.toml file
  * region - if other than us-east-1
  * parameter overrides
    * SlackChannel - slack Channel to send notifications to
    * SlackWebhookUrl - slack webhook url for the above channel
    * DomainNameList - comma separated list of OS domain names to monitor
* deploy the lambda using SAM: `./utils/deploy.sh default`

This will deploy/update the lambda.
