import requests
"""
#Register user with API server
register_url = 'http://127.0.0.1:5000/api/users'
headers = { 'Content-Type': 'application/json' }
data = '{"username":"john","password":"python"}'
rr = requests.post(register_url, headers=headers, data=data)
"""

#Get token
token_url = 'http://127.0.0.1:5000/api/token'
tr = requests.get(token_url, auth=('john', 'python'))
if tr.status_code == 200:
    token = str(tr.json()['token'])
    print "token=", token
else:
    token = ""


#Using static token to test client side code
#token = "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyMDExMDM3NSwiaWF0IjoxNTIwMTA5Nzc1fQ.eyJpZCI6NX0.QqHD7k4R6nQIvTQl7ZoLNHLr0iG_SZ3oV11tT62IzlM"

#get data using token
server_url = 'http://127.0.0.1:5000/api/test/getCount'
dr = requests.get(server_url, auth=(token, 'unused'))
if dr.status_code == 200:
    count = dr.json()['count']
    print "count=", count
else:
    print "error retriving data at", server_url
    print dr.json()


#logic to deal with start/stop of EC2 worker servers depending upon input
#1)If count = 0 , stop all EC2 servers (will need to get a status of EC2 servers
#based on tags to see if they are up or down
#2) Check how many EC2 servers are up (1,2 ..n) and store that value
#if input is less than max threahold, increment EC2 server value upto max threshold
# If max threahold reached, ignore all increments.

def get_next_worker(ec2_status):
    '''  returns next worker name '''
    n = int(sorted(ec2_status, key=lambda x:x[0])[-1][-1])+1
    return "testWorker" + str(n)
    

max_workers = 2   #maximum worker nodes that can be up 
ec2_status = {"testWorker1":0, "testWorker2":0}   #current worker_nodes status
                                                  #generate this dynamically

current_up_workers = sum(ec2_status.values())  #current up worker_nodes
if current_up_workers >= max_workers  and count != 0 : #max worker_nodes up
    print "current_up_workers = {} , max limit of {} reached, ignoring worker add request".format(current_up_workers,max_workers)
    
    
elif current_up_workers <= max_workers and count != 0: #add workers upto max limit
    print "adding  available worker to the pool"
    while count <= 1:
        if current_up_workers >= max_workers:
            print "Max worker limit reached."
            break
        new_worker = get_next_worker(ec2_status)
        print "Adding next_worker {}".format(new_worker)
        ec2_status[new_worker] = 1
        count -= 1
        

elif count == 0:  # irrespective of current worker status stop all EC2 instances
    
        
    print "stopping current_up_workers = {}".format(current_up_workers)
    for worker in ec2_status.keys():
        print "stopping worker {}".format(worker)
        ec2_status[worker] = 0
        
        if current_up_workers == 0:
            print "All workers now stopped"
            break
    
    


        
    




