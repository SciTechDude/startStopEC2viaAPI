"""
Module accesses AWS EC2 instance using BOTO3 via token and received a value.
If value is non-zero corresponding number of instances are started
If value is zero, all instances are stopped
"""
import sys
import logging
import boto3
import requests
from ec2StartStopConfig import *


def stop_instance(stop_id):
    '''
    Stop a given instance
    Expects instance_id of instance to stop
    Returns response after attempt to stop given instance
    '''
    instance_to_stop = EC2.Instance(stop_id)
    logging.info("stopping running instance %s", stop_id)
    stop_response = instance_to_stop.stop()
    return stop_response


def start_instance(start_id):
    '''
    Start a given instance
    Expects instance_id of instance to start
    Returns response after attempt to start given instance
    '''
    instance_to_start = EC2.Instance(start_id)
    logging.info("starting stopped instance %s", start_id)
    start_response = instance_to_start.start()
    return start_response


def get_count(url, api_token):
    '''
    Get server count from api data
    Expects API url and valid token
    Returns server_count on sucess, exit & end script on error
    '''
    api_call_response = get_api_data(url, api_token)
    if api_call_response.status_code == 200:
        if 'errorCode' in api_call_response.json():
            logging.error("API server responded with error")
            logging.error(api_call_response.json())
            sys.exit(1)
        elif 'count' in api_call_response.json():
            return api_call_response.json()['count']
    #error occured while parsing API data
    else:
        return api_call_response.json()


def get_api_data(url, server_token):
    '''
    Get API data using token
    Expects API url and valid token
    Returns api data on success and end script on error
    '''
    try:
        server_response = requests.get(url, auth=(server_token, 'unused'))
    #takes care of API server inaccessible exception.
    except:
        logging.error("Error, Could not access url %s", url)
        logging.error("URL may be inaccessible or token may have expired")
        logging.error(sys.exc_info()[0])
        sys.exit(1)
    return server_response


def main():
    ''' main function '''
    #Setup logging
    logging.basicConfig(level=logging.INFO)

    #Connect to EC2 using BOTO3
    global EC2
    EC2 = boto3.resource(ENV_TYPE, region_name=REGION)

    try:
        API_VALUE = get_count(SERVER_URL, TOKEN)
        logging.info("Server count received from API server : %s ", API_VALUE)
    except ValueError as VALUE:
        logging.error("Error, Could not access url %s , using given token", SERVER_URL)
        logging.error("URL may be inaccessible or token may have expired")
        logging.error(VALUE)
        return


    #Collect status of exisitng EC2 instances info in a list of dicts
    instance_status = []
    for instance in EC2.instances.filter():
        instance_tag_key = instance.tags[0]['Key']
        instance_tag_value = instance.tags[0]['Value']

        #Append to dict only data for needed tags key;value pair
        if instance_tag_key == TAG_KEY and instance_tag_value == TAG_VALUE:
            tempdict = dict()
            tempdict['instance_id'] = instance.id
            tempdict['instance_state'] = instance.state['Name']
            tempdict['instance_type'] = instance.instance_type
            instance_status.append(tempdict)

    #display available instances and their status
    logging.info("Available instances")
    for i in instance_status:
        logging.info(i)

    #Logic to manipulate EC2 instances based on  API_VALUE
    #API_VALUE 0, Stop all instances
    if API_VALUE == 0:
        #Get list of  running instance_id
        running_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'running']
        if running_instance_ids:
            for idx, instance_id in enumerate(running_instance_ids):
                logging.info("Stopping instances %s out of %s ", idx+1, len(running_instance_ids))
                response = stop_instance(instance_id)
                logging.info(response)
        else:
            logging.info("All instances for given tag are already in 'stopped' status")

    #API_VALUE non_zero, start desired instances only if instances available to start
    if API_VALUE != 0:
        #Get a list of 'stopped' instance
        stopped_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'stopped']
        if stopped_instance_ids:
            #Throw warning if instances available to start are less than desired
            if len(stopped_instance_ids) < API_VALUE:
                logging.info("Desired instances to start (%s) > available (%s)", API_VALUE, len(stopped_instance_ids))
                logging.info("You may want to add more instance to the setup")
                logging.info("As script will start only available instances")

            for count, instance_id in zip(range(API_VALUE), stopped_instance_ids):
                logging.info("Starting instances %s out of %s", count+1, len(stopped_instance_ids))
                response = start_instance(instance_id)
                logging.info(response)
        else:
            logging.info("All available instances already in 'running' state")
    return 0

if __name__ == "__main__":
    #Execute main function
    main()
