# es-service-updater

Send notifcation to specified slack channel every monday 9am if there is a update avaliable for elastic search in prod us-east-1 or us-west-2

* To push update to lambda

* run ./deploy.sh {s3-bucket} {env} {region} {lambda-prefix} "SlackChannel={channelname} DomainName={elastic domain name} Region={region} SlackWebhookUrl={slackwebhookurl}"

