########### Python 2.7 #############
import httplib, urllib, base64

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '10f509acd57e49eba47336f781327d77',
}

params = urllib.urlencode({
})

try:
    conn = httplib.HTTPSConnection('api.projectoxford.ai')
    conn.request("POST", "/speech/v0/internalIssueToken?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))



import httplib, json, urllib

class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


clientId = "YOUR AZURE SUBSCRIPTION ID"
clientSecret = "YOUR PRIMARY API KEY"
ttsHost = "https://speech.platform.bing.com"

params = urllib.urlencode({'grant_type': 'client_credentials', 'client_id': clientId, 'client_secret': clientSecret, 'scope': ttsHost})

print ("The body data: %s" %(params))

headers = {"Content-type": "application/x-www-form-urlencoded"}

AccessTokenHost = "oxford-speech.cloudapp.net"
path = "/token/issueToken"

# Connect to server to get the Oxford Access Token
conn = httplib.HTTPSConnection(AccessTokenHost)
conn.request("POST", path, params, headers)
response = conn.getresponse()
print(response.status, response.reason)

data = response.read()
conn.close()
accesstoken = data.decode("UTF-8")
print ("Oxford Access Token: " + accesstoken)

#decode the object from json
ddata=json.loads(accesstoken)
access_token = ddata['access_token']

# Read the binary from wave file
f = open('file.wav','rb')
try:
    body = f.read();
finally:
    f.close()

headers = {"Content-type": "audio/wav; samplerate=8000",
"Authorization": "Bearer " + access_token}

#Connect to server to recognize the wave binary
conn = httplib.HTTPSConnection("speech.platform.bing.com")
conn.request("POST", "/recognize/query?scenarios=ulm&appid=D4D52672-91D7-4C74-8AD8-42B1D98141A5&locale=en-US&device.os=wp7&version=3.0&format=json&requestid=1d4b6030-9099-11e0-91e4-0800200c9a66&instanceid=1d4b6030-9099-11e0-91e4-0800200c9a66", body, headers)
response = conn.getresponse()
print(response.status, response.reason)
data = response.read()
print(data)
conn.close()
px = Payload(data)
print px.header["lexical"]


