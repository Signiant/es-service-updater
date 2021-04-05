import logging.handlers
import argparse
import boto3
import re
import os
import json
import urllib

logging.getLogger().setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main lambda handler
    :param event:
    :param context:
    :return:
    """

    if 'SLACK_CHANNEL' in os.environ:
        slack_channel = os.environ['SLACK_CHANNEL']

    if 'DOMAIN_NAME_LIST' in os.environ:
        domain_name_list = os.environ['DOMAIN_NAME_LIST']

    if 'REGION' in os.environ:
        region = os.environ['REGION']

    if 'SLACK_WEBHOOK_URL' in os.environ:
        slack_webhook = os.environ['SLACK_WEBHOOK_URL']

    logging.info("AWS Region: {0}".format(region))
    SESSION = boto3.session.Session(region_name=region)
    es_client = SESSION.client('es')
    #domain_name_list is list of elastic domain seperated by space in prod
    domain_name_list=domain_name_list.split(",")
    for domain_name in domain_name_list:
        check_es_service_software_version(es_client, domain_name, region, slack_webhook, slack_channel)
        check_es_version(es_client, domain_name, region, slack_webhook, slack_channel)


def check_es_service_software_version(cf, domain_name, region, slack_webhook, slack_channel):
    logging.info("Check service software update for elasticsearch: {0} ".format(domain_name))
    response = cf.describe_elasticsearch_domain(DomainName=domain_name)
    service_software_options = response['DomainStatus']['ServiceSoftwareOptions']
    service_software_update_available = service_software_options['UpdateAvailable']
    logging.info("Update avaliable: {0} ".format(service_software_update_available))
    if service_software_update_available:
        current_version = service_software_options['CurrentVersion']
        new_version = service_software_options['NewVersion']
        slack_txt = "*Service Software update avaliable for:* {0}. \n*Current Version:* {1} \n*New Version:* {2}".format(
            domain_name, current_version, new_version)

        url_format = "https://console.aws.amazon.com/es/home?region={0}#domain:resource={1};action=dashboard;tab=undefined".format(
            region, domain_name)
        slack_message = {
            'channel': slack_channel,
            'text': slack_txt,
            "attachments": [
                {
                    "fallback": "Update the domain through AWS elastic Search Service Console",
                    "actions": [
                        {
                            "type": "button",
                            "text": "Press Here to Update",
                            "url": url_format
                        }
                    ]
                }
            ]
        }
        data = json.dumps(slack_message).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(slack_webhook, data, headers)
        resp = urllib.request.urlopen(req)
        response = resp.read()
        print(response)


def check_es_version(es_client, domain_name, region, slack_webhook, slack_channel):
    logging.info("Check service software update for elasticsearch: {0} ".format(domain_name))
    response = es_client.get_compatible_elasticsearch_versions(DomainName=domain_name)
    source_version=response['CompatibleElasticsearchVersions'][0]['SourceVersion']
    compatible_target_versions = response['CompatibleElasticsearchVersions'][0]['TargetVersions']

    if len(compatible_target_versions)==0:
        print("Domain: {} is already on latest version of Elasticsearch".format(domain_name))
    else:
        latest_version = compatible_target_versions[-1]
        print("Latest version of elastic Search that is compatible with Domain {0} is: {1}".format(domain_name,latest_version))

        slack_txt = "*Elasticsearch Version update avaliable for:* {0}. \n*Source Version:* {1} \n*Latest Version:* {2} \nIn AWS console Press 'Actions' -> 'Upgrade domain'".format(
            domain_name, source_version, latest_version)

        url_format = "https://console.aws.amazon.com/es/home?region={0}#domain:resource={1};action=dashboard;tab=undefined".format(
            region, domain_name)
        slack_message = {
            'channel': slack_channel,
            'text': slack_txt,
            "attachments": [
                {
                    "fallback": "Update the domain through AWS elastic Search Service Console",
                    "actions": [
                        {
                            "type": "button",
                            "text": "AWS Console",
                            "url": url_format
                        }
                    ]
                }
            ]
        }
        data = json.dumps(slack_message).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(slack_webhook, data, headers)
        resp = urllib.request.urlopen(req)
        response = resp.read()
        print(response)




if __name__ == "__main__":

    LOG_FILENAME = 'cloudformation_get_es_update_status.log'

    parser = argparse.ArgumentParser(description='Get ElasticSearch Service Update Status ')

    # parser.add_argument("--aws-access-key-id", help="AWS Access Key ID", dest='aws_access_key', required=False)
    # parser.add_argument("--aws-secret-access-key", help="AWS Secret Access Key", dest='aws_secret_key',
    #                      required=False)
    parser.add_argument("--domain-name-list", help="The domain name in elastic search that requires update ",
                        dest='domain_name_list',
                        required=False)
    parser.add_argument("--region", help="The AWS region the stack is in", dest='region', required=True)
    parser.add_argument("--profile", help="The name of an aws cli profile to use.", dest='profile', default=None,
                        required=True)
    parser.add_argument("--verbose", help="Turn on DEBUG logging", action='store_true', required=False)
    parser.add_argument("--dryrun", help="Do a dryrun - no changes will be performed", dest='dryrun',
                        action='store_true', default=False, required=False)
    args = parser.parse_args()
    log_level = logging.INFO

    if args.verbose:
        print("Verbose logging selected")
        log_level = logging.DEBUG

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5242880, backupCount=5)
    fh.setLevel(logging.DEBUG)
    # create console handler using level set in log_level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)8s: %(message)s')
    ch.setFormatter(console_formatter)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)8s: %(message)s')
    fh.setFormatter(file_formatter)
    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # create the session for the boto3 with profile and region from user parameters
    SESSION = boto3.session.Session(profile_name=args.profile, region_name=args.region)
    logging.info("AWS Region: {0}".format(args.region))

    es_client = SESSION.client('es')
    #domain_name_list is list of elastic domain seperated by space in prod
    domain_name_list=args.domain_name_list.split(",")
    for domain_name in domain_name_list:
        #DOn't commit this
        check_es_service_software_version(es_client, domain_name, args.region, "<your slack webhook>", "#slack-testing")
        check_es_version(es_client, domain_name, args.region, "<your slack webhook>", "#slack-testing")


