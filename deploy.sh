#!/bin/bash


deploy_bucket=$1
profile=$2
region=$3
prefix_name=$4
parameters=$5

rm -rf package

mkdir package

cp es_service_updater.py package/

cd package
    echo "Gathering requirements..."
    pip install -r ../requirements.txt --target .
cd ..

# Package up lambda code example:
# --s3-bucket dev2-useast1-lambda-deploy
# --profile dev2 --region us-east-1

echo "Packaging up lambda for deployment..."
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket $deploy_bucket \
    --s3-prefix es-service-updater \
    --output-template-file packaged-template.yaml \
    --profile $profile --region $region

RETCODE=$?
if [ $RETCODE -ne 0 ]; then
    echo "Failed to create package"
    exit $RETCODE
fi

# Deploy the lambda
# stack-name {stackname for the lambda}
# --parameter-overrides Region=us-east-1 DomainName=https://example.com
echo "Deploying lambda..."
aws cloudformation deploy --capabilities CAPABILITY_IAM  \
    --template-file ./packaged-template.yaml \
    --stack-name es-service-update-notification-${prefix_name}  \
    --parameter-overrides $parameters \
    --profile $profile  --region $region
RETCODE=$?
if [ $RETCODE -ne 0 ]; then
    echo "Failed to deploy lambda package"
    exit $RETCODE
fi
