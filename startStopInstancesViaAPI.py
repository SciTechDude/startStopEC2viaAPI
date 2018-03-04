"""
Module accesses AWS EC2 instance using BOTO3 via token and received a value.
If value is non-zero corresponding number of instances are started
If value is zero, all instances are stopped
"""



def stop_instance(stop_id):
    """
    Stop a given instance
    Expects instance_id of instance to stop
    Returns response after attempt to stop given instance
    """
    instance_to_stop = ec2.Instance(stop_id)
    print "stopping running instance {}".format(stop_id)
    stop_response = instance_to_stop.stop()
    return stop_response

def start_instance(start_id):
    """
    Start a given instance
    Expects instance_id of instance to start
    Returns response after attempt to start given instance
    """
    instance_to_start = ec2.Instance(start_id)
    print "starting stopped instance {}".format(start_id)
    start_response = instance_to_start.start()
    return start_response

def get_count(url, token):    
    '''
    Get server count from api data
    Expects API url and valid token
    Returns server_count on sucess, exit end script on error 
    '''
    api_call_response = get_api_data(url, token)
    if api_call_response.status_code == 200:
        if 'errorCode' in api_call_response.json():
            print "API server responded with error"
            print api_call_response.json()
            sys.exit(1)
        elif 'count' in api_call_response.json():
            return api_call_response.json()['count']        
    else:
        #error occured while parsing API data
        return api_call_response.json()

def get_api_data(url, token):    
    '''
    Get API data using token
    Expects API url and valid token
    Returns api data on success and end script on error 
    '''
    try:
        server_response = requests.get(url, auth=(token, 'unused'))
    except:  #takes care of API server inaccessible exception.
        print "Error, Could not access url {}".format(server_url)
        print "URL may be inaccessible or token may have expired"
        print "",format(sys.exc_info()[0])
        #raise SystemExit
        sys.exit(1)
    return server_response

      
def main():
    """ main function """
    try:
        API_VALUE = get_count(server_url, token)
        print "Server count received from API server : {}".format(API_VALUE)
    except ValueError as v:
        print "Error, Could not access url {} , using given token".format(server_url)
        print "URL may be inaccessible or token may have expired"
        print "Actual Error:", v
        return

    #Collect status of exisitng EC2 instances info in a list of dicts
    instance_status = []
    for instance in ec2.instances.filter():
        instance_tag_key = instance.tags[0]['Key']
        instance_tag_value = instance.tags[0]['Value']

        #Append to dict only data for needed tags key;value pair
        if instance_tag_key == TAG_KEY and instance_tag_value == TAG_VALUE:
            tempdict = dict()
            tempdict['instance_id'] = instance.id
            tempdict['instance_state'] = instance.state['Name']
            tempdict['instance_type'] = instance.instance_type
            instance_status.append(tempdict)

    #print available instances and their status
    print "Available instances"
    for i in instance_status: print i

    #Logic to manipulate EC2 instances based on  API_VALUE
    #API_VALUE 0, Stop all instances
    if API_VALUE == 0:
        #Get list of  running instance_id
        running_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'running']
        if running_instance_ids:
            for idx, instance_id in enumerate(running_instance_ids):
                print "Stopping instances {} out of {}".format(idx+1, len(running_instance_ids))
                response = stop_instance(instance_id)
                print response
        else:
            print "All instances for given tag are already in 'stopped' status"

    #API_VALUE non_zero, start desired instances only if instances available to start
    if API_VALUE != 0:        
        #Get a list of 'stopped' instance
        stopped_instance_ids = [i['instance_id']
                                for i in instance_status if i['instance_state'] == 'stopped']

        if  stopped_instance_ids:
            #Throw warning if instances available to start are less than desired
            if len(stopped_instance_ids) < API_VALUE:
                print "Desired instances to start ({}) < available ({})".format(API_VALUE, len(stopped_instance_ids))
                print "You may want to add more instance to the setup"
                print "As script will start only available instances"
            
            for count, instance_id in zip(range(API_VALUE), stopped_instance_ids):
                print "Starting instances {} out of {}".format(count+1, len(stopped_instance_ids))
                response = start_instance(instance_id)
                print response
        else:
            print "No instances available to start"
    return 0
                    
if __name__ == "__main__":    
    import boto3
    import requests
    import sys
    import logging

    #Setup logging
    logger.setLevel(logging.DEBUG)
    #fh = logging.FileHandler('startStopInstancesViaAPI.log')
    
    #User defined constants
    TAG_KEY = 'testServerType'
    TAG_VALUE = 'testWorker'
    REGION = 'us-east-2'
    ENV_TYPE = 'ec2'
    #API_VALUE = 0

    #Using static token to test client side code
    token = "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyMDE5MTEzMiwiaWF0IjoxNTIwMTkwNTMyfQ.eyJpZCI6NX0.GbhVX38qpjdfxNQd0CIE5aGH0p53LyCAsrJBbK9AqoQ"
    server_url = 'http://127.0.0.1:5000/api/test/getCount'
    
    #Connect to EC2 using BOTO3
    ec2 = boto3.resource(ENV_TYPE, region_name=REGION)

    #Execute main function
    main()
    
    
    
