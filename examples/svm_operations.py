from textwrap import indent
import requests, base64
import json
import sys
import time
import traceback
from docopt import docopt
from prettytable import PrettyTable
from utils import *
requests.packages.urllib3.disable_warnings()



def get_args():

	usage = """
	Usage:
		svm_operations.py -s <STORAGE> -VM <SVM> --create
		svm_operations.py -s <STORAGE> -VM <SVM> --remove
		svm_operations.py -s <STORAGE> -VM <SVM> --details
		svm_operations.py -s <STORAGE> -VM <SVM> --stop
		svm_operations.py -s <STORAGE> -VM <SVM> --start


		svm_operations.py --version
		svm_operations.py -h | --help

	Options:
		-h --help            Show this message and exit
		-s <STORAGE>         ZFS appliance/storage name

	"""
	# version = '{} VER: {} REV: {}'.format(__program__, __version__, __revision__)
	# args = docopt(usage, version=version)
	args = docopt(usage)
	return args	





def	create_svm(svm,storage):

    message = check_svm(svm, storage)
    if message['code'] == 0:
        print(message['message'])
        sys.exit(0)

    data = {
        "name" : svm,
        "snapshot_policy" :{
                'name':'default'
        },
    }

    data_ = json.dumps(data)
    url = 'https://'+storage
    headers = Headers()
    try:
        if svm.isalnum():
            t = PrettyTable()
            r = requests.post(url+'/api/svm/svms', data = data_,
                                verify=False, headers = headers)

            print('-'*50)
            resp={}
            d = r.json()
            url1 = 'https://'+storage+ d['job']['_links']['self']['href']
            req = requests.get(url1,verify=False, headers = headers)
            data1 = req.json()
            resp.update(data1)

            t.field_names = [
            'SVM',
            'Status',
            'Details'
            ]

            t.add_row(
                [svm,
                resp['state'],
                resp['start_time'],
                ]
                )
            print(t)


        else:
            print('SVM name is not valid!')

        
    except Exception as e:
        print(e)
        sys.exit(1)

def delete_svm(svm,storage):
    message = check_svm(svm, storage)

    if message['code'] == 1:
        print(message['message'])
        sys.exit(0)
    
    t = PrettyTable()
    uuid = get_svmUUID(svm,storage)

    data = {
        "uuid" : uuid
    }

    data_ = json.dumps(data)
    url = 'https://'+storage
    headers = Headers()

    r = requests.delete(url+'/api/svm/svms', data = data_,
					 verify=False, headers = headers)

    resp2={}


    d = r.json()
    url1 = 'https://'+storage+ d['job']['_links']['self']['href']
    newresp = requests.get(url1,verify=False, headers = headers)
    d = newresp.json()
    resp2.update(d)

    t.field_names = [
			'SVM name',
			'State',
			'Details',
			'Mesage'
			]

    t.add_row(
			[
			svm,
			resp2['uuid'],
			resp2['description'],
			'DELETED',
			]
		)
    print(t)


def details_svm(svm,storage):

    url = 'https://'+storage
    headers = Headers()
    
    message = check_svm(svm, storage)
    if message['code'] == 1:
        print(message['message'])
        sys.exit(0)

    try:
        r = requests.get(url+'/api/svm/svms?name='+svm,
                            verify=False, headers = headers)

    
    except requests.exceptions.ConnectionError as err:
        print(err)
        print('Cant connect to the storage!')
        sys.exit(1)

    except IndexError as err:
        print(err)
        print('SVM not found!')
        sys.exit(1)

    except json.decoder.JSONDecodeError as err:
        print(err)
        print('Cant connect to the storage!')
        sys.exit(1)

    except requests.exceptions.HTTPError as err:
        print(err)
        print('Cant connect to the storage!')
        sys.exit(1)

    except requests.exceptions.RequestException as err:
        print(err)
        print('Cant connect to the storage!')
        sys.exit(1)
    except Exception as err:
        print(err)
        sys.exit(1)

    respjson = r.json()
    if respjson['num_records'] != 0:

        uuid = respjson['records'][0]['uuid']
        
        resp = requests.get(url+'/api/svm/svms/'+uuid,
                                verify=False, headers = headers)
        resp_ = json.dumps(resp.json(), ensure_ascii=True, indent=4)
        print(resp_)


def stop_svm(svm,storage):
    message = check_svm(svm, storage)

    if message['code'] == 1:
        print(message['message'])
        sys.exit(0)

    uuid = get_svmUUID(svm,storage)

    data = {
        "state" : "stopped",
        "comment": "This SVM is stopped."
    }

    data_ = json.dumps(data)
    url = 'https://'+storage
    headers = Headers()

    try:
    
        r = requests.patch(url+'/api/svm/svms/'+uuid, data = data_,
                        verify=False, headers = headers)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    except Exception as err:
        print(err)
        sys.exit(1)    

    url_text = r.json()   
    job_status = "https://{}{}".format(storage,
                            url_text['job']['_links']['self']['href'])
    try:
        job_response = requests.get(
            job_status, headers=headers, verify=False)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    url_text = job_response.json()
    print('Stopping the svm . . .')
    jobstat_(url_text, headers, storage)




def start_svm(svm,storage):

    message = check_svm(svm, storage)

    if message['code'] == 1:
        print(message['message'])
        sys.exit(0)

    uuid = get_svmUUID(svm,storage)

    data = {
        "state" : "running",
        "comment": "This SVM is running."
    }

    data_ = json.dumps(data)
    url = 'https://'+storage
    headers = Headers()

    try:
    
        r = requests.patch(url+'/api/svm/svms/'+uuid, data = data_,
                        verify=False, headers = headers)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    except Exception as err:
        print(err)
        sys.exit(1)    

    url_text = r.json()   
    job_status = "https://{}{}".format(storage,
                            url_text['job']['_links']['self']['href'])
    try:
        job_response = requests.get(
            job_status, headers=headers, verify=False)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    url_text = job_response.json()
    print('starting the svm . . .')

    jobstat_(url_text, headers, storage)





def main(args):
    storage = args['<STORAGE>']
    svm_name = args['<SVM>']


    if args['--create']:
        create_svm(svm_name,storage)

    elif args['--remove']:
        delete_svm(svm_name,storage)

    elif args['--details']:
        details_svm(svm_name,storage)

    elif args['--stop']:
        stop_svm(svm_name,storage)

    elif args['--start']:
        start_svm(svm_name,storage)

if __name__ == '__main__':
	try:
		ARGS = get_args()

		main(ARGS)
	except KeyboardInterrupt:
		print('\nReceived Ctrl^C. Exiting....')
	except Exception:
		ETRACE = traceback.format_exc()
		print(ETRACE)