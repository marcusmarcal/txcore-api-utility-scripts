import json
import os
import requests
import time

from dotenv import load_dotenv
load_dotenv()

api_token = os.environ.get('BEARER_TOKEN_DEV')
int_passphrase = os.environ.get('INTERNALSRTPASSPHRASE')
api_headers = {
    'Authorization': 'Bearer {0}'.format(api_token),
    'Content-Type': 'application/json'
}
mwedge_ids = {
    'inx01': os.environ.get('INXMWEDGE01'),
    'inx02': os.environ.get('INXMWEDGE02'),
    'inx03': os.environ.get('INXMWEDGE03'),
    'eqp01': os.environ.get('EQPMWEDGE01'),
    'eqp02': os.environ.get('EQPMWEDGE02'),
    'eqp03': os.environ.get('EQPMWEDGE03'),
    'ave01': os.environ.get('AVEMWEDGE01'),
    'ave02': os.environ.get('AVEMWEDGE02'),
    'lmk01': os.environ.get('LMKMWEDGE01'),
    'lmk02': os.environ.get('LMKMWEDGE02'),
    'yer01': os.environ.get('YERMWEDGE01'),
    'yer02': os.environ.get('YERMWEDGE02'),
    'dev01': os.environ.get('DEVMWEDGE01'),
}
mwedge_ext_ips = {
    'inx01_ip': os.environ.get('INXMWEDGEIP01'),
    'inx02_ip': os.environ.get('INXMWEDGEIP02'),
    'inx03_ip': os.environ.get('INXMWEDGEIP03'),
    'eqp01_ip': os.environ.get('EQPMWEDGEIP01'),
    'eqp02_ip': os.environ.get('EQPMWEDGEIP02'),
    'eqp03_ip': os.environ.get('EQPMWEDGEIP03'),
}
mwedge_net_int = {
    'eqp01_srt': os.environ.get('EQPSRT01'),
    'eqp02_srt': os.environ.get('EQPSRT02'),
    'eqp03_srt': os.environ.get('EQPSRT03'),
    'ave01_srt': os.environ.get('AVESRT01'),
    'ave02_srt': os.environ.get('AVESRT02'),
    'ave01_udp': os.environ.get('AVEUDP01'),
    'ave02_udp': os.environ.get('AVEUDP02'),
    'lmk01_srt': os.environ.get('LMKSRT01'),
    'lmk02_srt': os.environ.get('LMKSRT02'),
    'lmk01_udp': os.environ.get('LMKUDP01'),
    'lmk02_udp': os.environ.get('LMKUDP02'),
    'yer01_srt': os.environ.get('YERSRT01'),
    'yer02_srt': os.environ.get('YERSRT02'),
    'yer01_udp': os.environ.get('YERUDP01'),
    'yer02_udp': os.environ.get('YERUDP02'),
}
api_urls = {
    'api_url_master': os.environ.get('APIURLMASTER'),
    'api_url_master_dev': os.environ.get('APIURLMASTERDEV'),
    'api_url_lon': os.environ.get('APIURLLON'),
    'api_url_ams': os.environ.get('APIURLAMS'),
    'api_url_fra': os.environ.get('APIURLFRA'),
}

#============ User Configuration START ============

api_url = api_urls['api_url_master_dev'] # set API endpoint
stream_count = 10 # total TXEdge stream count
first_ch = 1 # first channel of the range. 1 for building resources from scratch
sleep_time = 1 # delay between API calls in seconds
provider_name = 'VET' # 3 letters acronym
dev_edge_id = mwedge_ids['dev01'] # define which edge the contribution endpoint is set up, i.e. eqp01, eqp02 or eqp03
cont_passphrase = "jdfjdfgjrefjgdsljgredfgsdsferre3" # contribution SRT passphrase
cont_srt_type = 1 # contribution SRT endpoint type (0=Caller, 1=Listener)
dev_srt_caller_address = "" # DEV contribution SRT Caller endpoint address (if cont_srt_type = 0)
dev_srt_caller_port = 0 # DEV contribution SRT Caller endpoint port (if cont_srt_type = 0)
cont_srt_port = 3601 # SRT port numbering start (Listener type) or the relative port for Output +1000 on Caller mode
cont_srt_latency = 1000 # DEV contribution SRT endpoint latency
endpoint_paused = True # applied across all endpoints
endpoint_passive = False # applied only on regional sources
feed_thumbnails = True # applied across all streams
ave_udp_ip_13_oct = "231.216.17" # first 3 network address octets
lmk_udp_ip_13_oct = "226.1.17" # first 3 network address octets
yer_udp_ip_13_oct = "228.33.17" # first 3 network address octets
ave_udp_ip_4_oct = 1 # last network address octet
lmk_udp_ip_4_oct = 1 # last network address octet
yer_udp_ip_4_oct = 1 # last network address octet

#============ User Configuration END ============

start_time = time.time()
session = requests.Session()
session.headers.update(api_headers)

def backupPath(dev_edge_id):
    for i in range(stream_count):
        name_id = '{0:0>2}'.format(first_ch + i)

        # ==== DEV ====
        # DEV Stream
        request_body = {
            "name": f"DEV_{provider_name}_CH{name_id}",
            "enableThumbnails": feed_thumbnails
        }
        print("RequestBody:", request_body)
        create_stream = session.post(api_url + dev_edge_id + '/stream/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_stream.headers)
        print("ApiResponse:", json.loads(create_stream.text))
        print("StatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_stream.elapsed)
        eqp_stream_id = create_stream.json()['id']
        print("StreamID:", eqp_stream_id)
        print('====================================================')
        time.sleep(sleep_time)

        # DEV SRT Source
        if cont_srt_type == 0:
            address = dev_srt_caller_address
            port = dev_srt_caller_port
        elif cont_srt_type == 1:
            address = ""
            port = cont_srt_port
        else:
            print("Error: Wrong DEV SRT Type value")

        if dev_edge_id == mwedge_ids['dev01']:
            eqp_srt_host_address = mwedge_net_int['eqp01_srt']
        elif dev_edge_id == mwedge_ids['eqp02']:
            eqp_srt_host_address = mwedge_net_int['eqp02_srt']
        elif dev_edge_id == mwedge_ids['eqp03']:
            eqp_srt_host_address = mwedge_net_int['eqp03_srt']
        else:
            print("Error: Issue with DEV SRT Host IP")
        request_body = {
            "name": f"DEV_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(eqp_stream_id),
            "options": {
                 "address": address,
                 "port": port + i,
                 "hostAddress": eqp_srt_host_address,
                 "latency": cont_srt_latency,
                 "type": cont_srt_type,
                 "encryption": 32,
                 "passphrase": cont_passphrase
                 },
            "paused": endpoint_paused,
            "passive": endpoint_passive,
            "priority": 0,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + dev_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        eqp_source_id = create_source.json()['id']
        print("SourceID:", eqp_source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # DEV SRT Output
        request_body = {
            "name": f"DEV_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(eqp_stream_id),
            "options": {
                "port": cont_srt_port + 1000 + i,
                "hostAddress": eqp_srt_host_address,
                "encryption": 32,
                "passphrase": int_passphrase,
                "latency": 500,
                "type": 0
            },
            "paused": endpoint_paused
        }
        print("RequestBody:", request_body)
        create_output = session.post(api_url + dev_edge_id + '/output/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_output.headers)
        print("ApiResponse:", json.loads(create_output.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_output.elapsed)
        eqp_output_id = create_output.json()['id']
        print("OutputID:", eqp_output_id)
        print('====================================================')
        time.sleep(sleep_time)

# Call the function
backupPath(dev_edge_id)

end_time = time.time()
execution_time = end_time - start_time
print('Overall script execution time in seconds:', execution_time)
