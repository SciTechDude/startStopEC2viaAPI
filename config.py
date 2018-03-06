"""
Configure file to hold constant parameters,
Including Token and API_server_url
"""
#User defined constants
TAG_KEY = "testServerType"
TAG_VALUE = "testWorker"
REGION = "us-east-2"
ENV_TYPE = "ec2"

#Using static token to test client side code
TOKEN = "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyMDI5OTU2NCwiaWF0IjoxNTIwMjk4OTY0fQ.eyJpZCI6NH0.d17s-oH_07fVpHP9K9Z2cc5EAtaXXXD7Pm-Cn_buudE"

URL = "ec2-18-188-11-10.us-east-2.compute.amazonaws.com"
PORT = "5000"
API_LOC = "/api/test/getCount"
#SERVER_URL = "http://127.0.0.1:5000/api/test/getCount"
SERVER_URL = "http://" + URL + ":" + PORT  + API_LOC
