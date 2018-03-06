#http://boto3.readthedocs.io/en/latest/guide/migrationec2.html
#https://linuxacademy.com/howtoguides/posts/show/topic/14209-automating-aws-with-python-and-boto3

import requests
ip_address = "127.0.0.1"
#ip_address = "52.14.96.29"

#Register user with API server
register_url = 'http://{}:5000/api/users'.format(ip_address)
headers = { 'Content-Type': 'application/json' }
data = '{"username":"anil","password":"python"}'
rr = requests.post(register_url, headers=headers, data=data)


#Get token
token_url = 'http://{}:5000/api/token'.format(ip_address)
tr = requests.get(token_url, auth=('anil', 'python'))
if tr.status_code == 200:
    token = str(tr.json()['token'])
    print "token = ", token
else:
    token = ""

#get data using token
server_url = 'http://{}:5000/api/test/getCount'.format(ip_address)
dr = requests.get(server_url, auth=(token, 'unused'))
if dr.status_code == 200:
    API_VALUE = dr.json()['count']
    print "API_VALUE=", API_VALUE
    #return API_VALUE
else:
    print "error retriving data at", server_url
    print dr.json()
    #return dr.json()
