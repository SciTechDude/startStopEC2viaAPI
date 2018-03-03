import requests


#Register user with API server
register_url = 'http://127.0.0.1:5000/api/users'
headers = { 'Content-Type': 'application/json' }
data = '{"username":"john","password":"python"}'
rr = requests.post(register_url, headers=headers, data=data)


#Get token
token_url = 'http://127.0.0.1:5000/api/token'
tr = requests.get(token_url, auth=('john', 'python'))
if tr.status_code == 200:
    token = str(tr.json()['token'])
else:
    token = ""


#get data using token
count_url = 'http://127.0.0.1:5000/api/test/getCount'
dr = requests.get(count_url, auth=(token, 'unused'))
if dr.status_code == 200:
    count = dr.json()['count']
    print "count=", count
else:
    print "error retriving data"
