import json
import os
import requests
import time

api_token = os.environ.get('BEARER_TOKEN_PROD')
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
    'api_url_lon': os.environ.get('APIURLLON'),
    'api_url_ams': os.environ.get('APIURLAMS'),
    'api_url_fra': os.environ.get('APIURLFRA'),
}

#============ User Configuration START ============

api_url = api_urls['api_url_ams'] # set API endpoint
stream_count = 2 # total TXEdge stream count
sleep_time = 1 # delay between API calls in seconds
provider_name = 'TEST'
eqp_edge_id = mwedge_ids['eqp03'] # define which edge the contribution endpoint is set up, i.e. eqp01, eqp02 or eqp03
cont_passphrase = "cont_testpassphrase" # contribution SRT passphrase
cont_srt_type = 0 # contribution SRT endpoint type (0=Caller, 1=Listener)
eqp_srt_caller_address = "1.1.1.1" # EQP contribution SRT Caller endpoint address (if cont_srt_type = 0)
eqp_srt_caller_port = 4444 # EQP contribution SRT Caller endpoint port (if cont_srt_type = 0)
cont_srt_port = 1000 # SRT port numbering start (Listener type)
cont_srt_latency = 1000 # EQP contribution SRT endpoint latency
endpoint_paused = True # applied across all endpoints
endpoint_passive = False # applied only on regional sources
feed_thumbnails = True # applied across all streams
ave_udp_ip_13_oct = "231.216.10" # first 3 network address octets
lmk_udp_ip_13_oct = "226.1.10" # first 3 network address octets
yer_udp_ip_13_oct = "228.33.10" # first 3 network address octets
ave_udp_ip_4_oct = "1" # last network address octet
lmk_udp_ip_4_oct = "1" # last network address octet
yer_udp_ip_4_oct = "1" # last network address octet

#============ User Configuration END ============

start_time = time.time()
session = requests.Session()
session.headers.update(api_headers)

def backupPath(eqp_edge_id, ave01_edge_id=mwedge_ids['ave01'], lmk02_edge_id=mwedge_ids['lmk02'], yer02_edge_id=mwedge_ids['yer02']):
    for i in range(stream_count):
        name_id = '{0:0>2}'.format(i + 1)

        # ==== EQP ====
        # EQP Stream
        request_body = {
            "name": f"EQP_{provider_name}_CH{name_id}",
            "enableThumbnails": feed_thumbnails
        }
        print("RequestBody:", request_body)
        create_stream = session.post(api_url + eqp_edge_id + '/stream/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_stream.headers)
        print("ApiResponse:", json.loads(create_stream.text))
        print("StatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_stream.elapsed)
        eqp_stream_id = create_stream.json()['id']
        print("StreamID:", eqp_stream_id)
        print('====================================================')
        time.sleep(sleep_time)

        # EQP SRT Source
        if cont_srt_type == 0:
            address = eqp_srt_caller_address
            port = eqp_srt_caller_port
        elif cont_srt_type == 1:
            address = ""
            port = cont_srt_port
        else:
            print("Error: Wrong EQP SRT Type value")

        if eqp_edge_id == mwedge_ids['eqp01']:
            eqp_srt_host_address = mwedge_net_int['eqp01_srt']
        elif eqp_edge_id == mwedge_ids['eqp02']:
            eqp_srt_host_address = mwedge_net_int['eqp02_srt']
        elif eqp_edge_id == mwedge_ids['eqp03']:
            eqp_srt_host_address = mwedge_net_int['eqp03_srt']
        else:
            print("Error: Issue with EQP SRT Host IP")
        request_body = {
            "name": f"EQP_{provider_name}_CH{name_id}",
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
        create_source = session.post(api_url + eqp_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        eqp_source_id = create_source.json()['id']
        print("SourceID:", eqp_source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # EQP SRT Output
        request_body = {
            "name": f"EQP_{provider_name}_CH{name_id}",
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
        create_output = session.post(api_url + eqp_edge_id + '/output/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_output.headers)
        print("ApiResponse:", json.loads(create_output.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_output.elapsed)
        eqp_output_id = create_output.json()['id']
        print("OutputID:", eqp_output_id)
        print('====================================================')
        time.sleep(sleep_time)

        #  ==== Define SRT Caller IPs for Regional TXEdges  ====
        if eqp_edge_id == mwedge_ids['eqp01']:
            prim_address = mwedge_ext_ips['inx01_ip']
            back_address = mwedge_ext_ips['eqp01_ip']
        elif eqp_edge_id == mwedge_ids['eqp02']:
            prim_address = mwedge_ext_ips['inx02_ip']
            back_address = mwedge_ext_ips['eqp02_ip']
        elif eqp_edge_id == mwedge_ids['eqp03']:
            prim_address = mwedge_ext_ips['inx03_ip']
            back_address = mwedge_ext_ips['eqp03_ip']
        else:
            print("Error: Issue with SRT Caller IPs for Regional TXEdges")

        # ==== AVE01 ====
        # AVE01 Stream
        request_body = {
            "name": f"AVE_INX_{provider_name}_CH{name_id}",
            "enableThumbnails": feed_thumbnails
        }
        print("RequestBody:", request_body)
        create_stream = session.post(api_url + ave01_edge_id + '/stream/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_stream.headers)
        print("ApiResponse:", json.loads(create_stream.text))
        print("StatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_stream.elapsed)
        ave01_stream_id = create_stream.json()['id']
        print("StreamID:", ave01_stream_id)
        print('====================================================')
        time.sleep(sleep_time)

        # AVE01 INX SRT Source
        request_body = {
            "name": f"AVE_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(ave01_stream_id),
            "options": {
                "address": prim_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['ave01_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 1,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + ave01_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # AVE01 EQP SRT Source
        request_body = {
            "name": f"zAVE_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(ave01_stream_id),
            "options": {
                "address": back_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['ave01_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 2,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + ave01_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # AVE01 UDP Output
        request_body = {
            "name": f"AVE_INX_{provider_name}_CH{name_id}",
            "protocol": "UDP",
            "stream": str(ave01_stream_id),
            "options": {
                "address": f"{ave_udp_ip_13_oct}.{i + 1}",
                "networkInterface": mwedge_net_int['ave01_udp'],
                "port": 1234,
            },
            "paused": endpoint_paused
        }
        print("RequestBody:", request_body)
        create_output = session.post(api_url + ave01_edge_id + '/output/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_output.headers)
        print("ApiResponse:", json.loads(create_output.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_output.elapsed)
        output_id = create_output.json()['id']
        print("OutputID:", output_id)
        print('====================================================')
        time.sleep(sleep_time)

        # ==== LMK02 ====
        # LMK02 Stream
        request_body = {
            "name": f"LMK_INX_{provider_name}_CH{name_id}",
            "enableThumbnails": feed_thumbnails
        }
        print("RequestBody:", request_body)
        create_stream = session.post(api_url + lmk02_edge_id + '/stream/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_stream.headers)
        print("ApiResponse:", json.loads(create_stream.text))
        print("StatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_stream.elapsed)
        lmk02_stream_id = create_stream.json()['id']
        print("StreamID:", lmk02_stream_id)
        print('====================================================')
        time.sleep(sleep_time)

        # LMK02 INX SRT Source
        request_body = {
            "name": f"LMK_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(lmk02_stream_id),
            "options": {
                "address": prim_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['lmk02_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 1,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + lmk02_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # LMK02 EQP SRT Source
        request_body = {
            "name": f"zLMK_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(lmk02_stream_id),
            "options": {
                "address": back_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['lmk02_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 2,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + lmk02_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # LMK02 UDP Output
        request_body = {
            "name": f"LMK_INX_{provider_name}_CH{name_id}",
            "protocol": "UDP",
            "stream": str(lmk02_stream_id),
            "options": {
                "address": f"{lmk_udp_ip_13_oct}.{i + 1}",
                "networkInterface": mwedge_net_int['lmk02_udp'],
                "port": 21216,
            },
            "paused": endpoint_paused
        }
        print("RequestBody:", request_body)
        create_output = session.post(api_url + lmk02_edge_id + '/output/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_output.headers)
        print("ApiResponse:", json.loads(create_output.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_output.elapsed)
        output_id = create_output.json()['id']
        print("OutputID:", output_id)
        print('====================================================')
        time.sleep(sleep_time)

        # ==== YER02 ====
        # YER02 Stream
        request_body = {
            "name": f"YER_INX_{provider_name}_CH{name_id}",
            "enableThumbnails": feed_thumbnails
        }
        print("RequestBody:", request_body)
        create_stream = session.post(api_url + yer02_edge_id + '/stream/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_stream.headers)
        print("ApiResponse:", json.loads(create_stream.text))
        print("StatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_stream.elapsed)
        yer02_stream_id = create_stream.json()['id']
        print("StreamID:", yer02_stream_id)
        print('====================================================')
        time.sleep(sleep_time)

        # YER02 INX SRT Source
        request_body = {
            "name": f"YER_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(yer02_stream_id),
            "options": {
                "address": prim_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['yer02_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 1,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + yer02_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # YER02 EQP SRT Source
        request_body = {
            "name": f"zYER_INX_{provider_name}_CH{name_id}",
            "protocol": "SRT",
            "stream": str(yer02_stream_id),
            "options": {
                "address": back_address,
                "port": cont_srt_port + 1000 + i,
                "hostAddress": mwedge_net_int['yer02_srt'],
                "latency": 500,
                "type": 0,
                "encryption": 32,
                "passphrase": int_passphrase
            },
            "paused": endpoint_paused,
            "passive": True,
            "priority": 2,
        }
        print("RequestBody:", request_body)
        create_source = session.post(api_url + yer02_edge_id + '/source/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_source.headers)
        print("ApiResponse:", json.loads(create_source.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_source.elapsed)
        source_id = create_source.json()['id']
        print("SourceID:", source_id)
        print('====================================================')
        time.sleep(sleep_time)

        # YER02 UDP Output
        request_body = {
            "name": f"YER_INX_{provider_name}_CH{name_id}",
            "protocol": "UDP",
            "stream": str(yer02_stream_id),
            "options": {
                "address": f"{yer_udp_ip_13_oct}.{i + 1}",
                "networkInterface": mwedge_net_int['yer02_udp'],
                "port": 1234,
            },
            "paused": endpoint_paused
        }
        print("RequestBody:", request_body)
        create_output = session.post(api_url + yer02_edge_id + '/output/', headers=api_headers, json=request_body)
        print("ResponseHeaders:", create_output.headers)
        print("ApiResponse:", json.loads(create_output.text))
        print("RequestStatusCode:", create_stream.status_code)
        print("RequestElapsedTime:", create_output.elapsed)
        output_id = create_output.json()['id']
        print("OutputID:", output_id)
        print('====================================================')
        time.sleep(sleep_time)

# Call the function
backupPath(eqp_edge_id)

end_time = time.time()
execution_time = end_time - start_time
print('Overall script execution time in seconds:', execution_time)
