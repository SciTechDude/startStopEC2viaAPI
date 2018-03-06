"""
Module accesses AWS EC2 instance using BOTO3 via token and received a value.
If value is non-zero corresponding number of instances are started
If value is zero, all instances are stopped
"""
from __future__ import print_function
import os
import logging
import sys
import boto3
from botocore.vendored import requests
#from config import *
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def stop_instance(stop_id):
    '''
    Stop a given instance
    Expects instance_id of instance to stop
    Returns response after attempt to stop given instance
    '''
    instance_to_stop = EC2.Instance(stop_id)
    logger.info("stopping running instance  %s", stop_id)
    stop_response = instance_to_stop.stop()
    return stop_response


def start_instance(start_id):
    '''
    Start a given instance
    Expects instance_id of instance to start
    Returns response after attempt to start given instance
    '''
    instance_to_start = EC2.Instance(start_id)
    logger.info("starting stopped instance %s", start_id)
    start_response = instance_to_start.start()
    return start_response


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
        logger.info("Error, Could not access url %s", url)
        logger.info(sys.exc_info()[0])
        return

    if server_response.status_code == 200:
        if 'errorCode' in server_response.json():
            logger.error("API server responded with error")
            return server_response.json()        
        elif 'count' in server_response.json():
            return server_response.json()['count']
    #error occured while parsing API data
    else:
        logger.error("API server responded with error")
        return server_response.json()

    logger.info("Server response", server_respone.json())
    return server_response


def main(event, context):
    ''' main function '''

    #Environment Variables
    
    TAG_KEY = os.environ["TAG_KEY"]
    TAG_VALUE = os.environ["TAG_VALUE"]
    REGION = os.environ["REGION"]
    ENV_TYPE = os.environ["ENV_TYPE"]
    PORT = os.environ["PORT"]
    API_LOC = os.environ["API_LOC"]
    TOKEN = os.environ["TOKEN"]
    SERVER_NAME = os.environ["SERVER_NAME"]
    SERVER_URL = "http://" + SERVER_NAME + ":" + PORT + API_LOC
    
    #Connect to EC2 using BOTO3
    global EC2
    EC2 = boto3.resource(ENV_TYPE, region_name=REGION)

    try:
        API_VALUE = get_api_data(SERVER_URL, TOKEN)

        logger.info("Server count received from API server: %s", API_VALUE)
    except ValueError as VALUE:
        logger.error("Could not access url %s", SERVER_URL)
        logger.error(" URL may be inaccessible or token may have expired")
        logger.error("%s", VALUE)
        return

    if not isinstance(API_VALUE, int):
        logger.error("Invalid Value returned from server")
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
    logger.info("Available instances")
    for i in instance_status:
        logger.info("%s", i)

    #Logic to manipulate EC2 instances based on  API_VALUE
    #API_VALUE 0, Stop all instances
    if API_VALUE == 0:
        #Get list of  running instance_id
        running_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'running']
        if running_instance_ids:
            for idx, instance_id in enumerate(running_instance_ids):
                logger.info("Stopping instances %s out of %s ",idx+1, len(running_instance_ids))
                response = stop_instance(instance_id)
                logger.info("%s",response)
        else:
            logger.info("All instances for given tag are already in 'stopped' status")

    #API_VALUE non_zero, start desired instances only if instances available to start
    if API_VALUE != 0:
        #Get a list of 'stopped' instance
        stopped_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'stopped']
        if stopped_instance_ids:
            #Throw warning if instances available to start are less than desired
            if len(stopped_instance_ids) < API_VALUE:
                logger.info("Desired instances to start (%s) > available (%s)",API_VALUE, len(stopped_instance_ids))
                logger.info("You may want to add more instance to the setup")

            for count, instance_id in zip(range(API_VALUE), stopped_instance_ids):
                logger.info("Starting instances %s out of %s",count+1, len(stopped_instance_ids))
                response = start_instance(instance_id)
                logger.info("%s",response)
        else:
            logger.info("All available instances already in 'running' state")
    return 0

"""
if __name__ == "__main__":
    main()
"""
