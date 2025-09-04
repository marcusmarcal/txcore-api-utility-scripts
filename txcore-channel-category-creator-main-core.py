import json
import os
import requests
import time

from dotenv import load_dotenv
load_dotenv()

#api_token = os.environ.get('BEARER_TOKEN_STB')
api_token = os.environ.get('BEARER_TOKEN_PROD')
#api_token = os.environ.get('BEARER_TOKEN_DEV')

#api_url_stb = os.environ.get('APIURLSTB')
api_url_stb = os.environ.get('APIURLPROD')
#api_url_stb = os.environ.get('APIURLDEV')

passphrase = os.environ.get('INTERNALSRTPASSPHRASE')

api_headers = {
    'Authorization': 'Bearer {0}'.format(api_token),
    'Content-Type': 'application/json'
}


#geofence_ids = {
#    'ave': os.environ.get('AVEGEOID'),
#    'lmk': os.environ.get('LMKGEOID'),
#    'yer': os.environ.get('YERGEOID'),
#    
#}

#============ Configurable items START ============

dry_run = False # True=no API calls are made, results are printed in console; False=normal operation
channel_count = 21 # total TXCore channel count
sleep_time = 1 # delay between API calls in seconds
first_ch = 1 # First channel of the range. 1 if creating from scratch. 
srt_source_ip = '194.76.59.21'
srt_first_port = 8101
provider_name = "XRU" # 3 letters acronym - No need to have _CH
channel_number = 7001 # channel numbering start
category_name = "Xeatre Rugby"
category_id = '68b846b1d126ad1c4638ef07' # use this only if category exists already

#ave_udp_ip_13_oct = "231.216.3" # first 3 network address octets
#lmk_udp_ip_13_oct = "226.1.2" # first 3 network address octets
#yer_udp_ip_13_oct = "228.33.3" # first 3 network address octets
#ave_udp_ip_4_oct = 243 # last network address octet
#lmk_udp_ip_4_oct = 253 # last network address octet
#yer_udp_ip_4_oct = 243 # last network address octet

#============ Configurable items END ============

start_time = time.time()

session = requests.Session()
session.headers.update(api_headers)

def createCategory(dry_run=False):
    request_body_cat = {
                "name": category_name,
                "desc": category_name
   }

    if dry_run:
        print("Dry run: Printing createCategory request body without making API request")
        print("Request body:", request_body_cat)
        print('====================================================')
        return None

    create_category = session.post(api_url_stb + '/category/', headers=api_headers, json=request_body_cat)
    print("ResponseHeaders:", create_category.headers)
    print("ApiResponse:", json.loads(create_category.text))
    print("RequestStatusCode:", create_category.status_code)
    print("RequestElapsedTime:", create_category.elapsed)
    category_id = create_category.json()['_id']
    print("CategoryID:", category_id)
    print('====================================================')
    return category_id

def createChannels(category_id, dry_run=False):
    for i in range(channel_count):
        name_id = '{0:0>2}'.format(first_ch + i)
        request_body = {
                    "number": channel_number + i,
                    "name": f"{provider_name}_CH{name_id}",
                    "type": 0,
                    "category": category_id,
                    "enabled": True,
                    "sources": [{
                                "protocol": 6,
                                "address": f"{srt_source_ip}:{srt_first_port + i}",
                                "options": {
                                    "srt": {
                                        "encrypted": True,
                                        "passphrase": passphrase
                                    }
                                }
                                #"geofence": geofence_ids['ave'] # Not needed for this workflow, in principle
                                }]

        }
        if dry_run:
            print("Dry run: Printing createChannels request body without making API request")
            print("Request body:", request_body)
            print('====================================================')
            continue

        print("RequestBody:", request_body)
        create_channel = session.post(api_url_stb + '/channel/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_channel.headers)
        print("ApiResponse:", json.loads(create_channel.text))
        print("StatusCode:", create_channel.status_code)
        print("RequestElapsedTime:", create_channel.elapsed)
        print('====================================================')
        time.sleep(sleep_time)

# Call the functions
# Comment this line category_id if category already created
#category_id = createCategory(dry_run=dry_run)
createChannels(category_id, dry_run=dry_run)

end_time = time.time()
execution_time = end_time - start_time
print('Overall script execution time in seconds:', execution_time)
