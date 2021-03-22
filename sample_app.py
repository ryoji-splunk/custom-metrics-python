#ADD NECESSARY IMPORTS FOR SENDING DATA TO SIGNALFX
import time
import requests
import signalfx
import ConfigParser
import sys
import os

config_parser = ConfigParser.SafeConfigParser()
config_parser.read(os.path.join(sys.path[0], 'sfx.conf'))


SFX_TOKEN = config_parser.get('credential', 'token')

SFX_REALM = config_parser.get('environment', 'realm')

API_ENDPOINT = "https://api.{}.signalfx.com".format(SFX_REALM)
INGEST_ENDPOINT = "https://ingest.{}.signalfx.com".format(SFX_REALM)
STREAM_ENDPOINT = "https://stream.{}.signalfx.com".format(SFX_REALM)

#INSTANTIATE THE SIGNALFX OBJECT
sfx = signalfx.SignalFx(api_endpoint=API_ENDPOINT,
        ingest_endpoint=INGEST_ENDPOINT,
        stream_endpoint=STREAM_ENDPOINT).ingest(SFX_TOKEN)

def getResponseTime(url):
   begin_url_time = time.time()
   try:
      res = requests.get(url)
      time_toget_url = (time.time()-begin_url_time)*1000  #Time is milliseconds
      tstamp=time.time()*1000
   except requests.exceptions.RequestException as e:  # This is the correct syntax
      raise SystemExit(e)
   return time_toget_url,tstamp,res.status_code

def main():
   try:  
      while True:
         now = int(time.time())
         if now % 5 == 0:   # Sending datapoints every 5 seconds
            sites = ['bing.com','google.com','yahoo.com','duckduckgo.com']
            for site in sites:
               starturl='http://%s'
               resp=getResponseTime(starturl % site)
               print("Site: " + starturl % site + " / ResponseTime: " + str(resp[0]))
               # Send datapoint / custom metric
               sfx.send(gauges=[
                                 {'metric': 'my_https_response_time',
                                 'value': resp[0],
                                 'timestamp': resp[1],
                                 'dimensions': {'site': site, 'env': "test", 'http_status_code': str(resp[2])}
                                 },
                              ])
   except KeyboardInterrupt:
      pass
 
if __name__ == '__main__':
    main()
