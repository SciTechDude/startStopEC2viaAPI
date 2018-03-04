#http://boto3.readthedocs.io/en/latest/guide/migrationec2.html
#https://linuxacademy.com/howtoguides/posts/show/topic/14209-automating-aws-with-python-and-boto3
import boto3
import requests

#User defined constants
TAG_KEY = 'testServerType'
TAG_VALUE = 'testWorker'
REGION = 'us-east-2'
ENV_TYPE = 'ec2'
#API_VALUE = 0

def stop_instance(instance_id):
    instance = ec2.Instance(instance_id)
    print "stopping running instance {}".format(instance_id)
    response = instance.stop()
    return response

def start_instance(instance_id):
    instance = ec2.Instance(instance_id)
    print "starting stopped instance {}".format(instance_id)
    response = instance.start()
    return response



#Using static token to test client side code
token="eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyMDE0MjY4OCwiaWF0IjoxNTIwMTQyMDg4fQ.eyJpZCI6NX0.eQ2ilXCLWdJ8kr59BH2Ky_sUCdbqN5qv0aNFCV3ulHs"
#get data using token
server_url = 'http://127.0.0.1:5000/api/test/getCount'
dr = requests.get(server_url, auth=(token, 'unused'))
if dr.status_code == 200:
    API_VALUE = dr.json()['count']
    print "API_VALUE=", API_VALUE
else:
    print "error retriving data at", server_url
    print dr.json()


#Connect to EC2 using BOTO3
ec2 = boto3.resource(ENV_TYPE, region_name=REGION)
#client = boto3.client(ENV_TYPE, region_name=REGION)


# Use the filter() method of the instances collection to retrieve
# all running EC2 instances.
#Collect status exisitng EC2 instances info in a list of dicts
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
    running_instance_ids = [i['instance_id'] for i in instance_status if i['instance_state'] == 'running' ]
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
    stopped_instance_ids = [i['instance_id'] for i in instance_status if i['instance_state'] == 'stopped']

    if  stopped_instance_ids:
        #Throw warning if instances available to start are less than desired
        if len(stopped_instance_ids) < API_VALUE:
            print "Desired instances to start ({}) is less than available ({})".format(API_VALUE,len(stopped_instance_ids))
            print "You may want to add more instance to the setup"
            print "As script will start only available instances"
        
        for count,instance_id in zip(range(API_VALUE),stopped_instance_ids):
        #for idx, instance_id in enumerate(stopped_instance_ids):
            print "Starting instances {} out of {}".format(count+1, len(stopped_instance_ids))
            response = start_instance(instance_id)
            print response
    else:
        print "No instances available to start"
                

    
    
