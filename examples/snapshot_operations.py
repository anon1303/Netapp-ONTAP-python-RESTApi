__program__ = 'Snapshot operations'
__version__ = 'Version 1'
__revision__ = 'Initial program'


import requests
import json
import traceback
from docopt import docopt
from prettytable import PrettyTable
from utils import *
requests.packages.urllib3.disable_warnings()



def get_args():

	usage = """
	Usage:
		Snapshot_operations.py -s <STORAGE> -vm <SVM> -vn <VOLUME_NAME> --create
		Snapshot_operations.py -s <STORAGE> -vm <SVM> -vn <VOLUME_NAME> --details
		Snapshot_operations.py -s <STORAGE> -vm <SVM> -vn <VOLUME_NAME> --list
		Snapshot_operations.py -s <STORAGE> -vm <SVM> -vn <VOLUME_NAME> --remove
		Snapshot_operations.py --version
		Snapshot_operations.py -h | --help

	Options:
		-h --help            Show this message and exit
		-s <STORAGE>         ZFS appliance/storage name
   
	"""
	version = '{} VER: {} REV: {}'.format(__program__, __version__, __revision__)
	args = docopt(usage, version=version)

	return args	

def create_snapshot(storage, svm, vol_name):
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    headers = res[1]

    url = "https://{}/api/storage/volumes/{}/snapshots".format(
                        storage, uuid)
    snap_name = input('Enter the name of SNAPSHOT: ')
    data = {}
    data['name'] = snap_name
    try:
        resp = requests.post(
            url,
            json=data,
            headers=headers,
            verify=False
        )
    except requests.exceptions.HTTPError as e:
        print(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except Exception as e:
        print('ssss')
        print(e)
        sys.exit(1)


    url_res = resp.json()
    if 'error' in url_res:
        print(url_res)
        sys.exit(1)
    
    elif 'job' in url_res:
        job_status = url_res
        jobstat(job_status, headers, storage)

    else:
        print('-'*50)
        print(url_res)
        sys.exit(1)

def list_snapshots(storage, svm, vol_name):
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    headers = res[1]

    url = "https://{}/api/storage/volumes/{}/snapshots".format(
                                storage, uuid)

    try:
        resp = requests.get(
            url,
            headers=headers,
            verify=False
        )
    except requests.exceptions.HTTPError as e:
        print(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except Exception as e:
        print(e)
        sys.exit(1)

    url_res = resp.json()
    if 'error' in url_res:
        print(url_res)
        sys.exit(1)
    
    data = dict(url_res)
    snapshots = data['records']
    t = PrettyTable(['UUID', 'Name'])

    for snap in snapshots:
        t.add_row([
            snap['uuid'],
            snap['name'],

        ])
    print(t)

# added get snapshot(28/9/22)
def get_snapshot(storage, svm, vol_name):
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    headers = res[1]

    snap_name = input('Enter the name of SNAPSHOT: ')
    snap_uuid = get_id_snapshot(storage, svm, vol_name,snap_name, headers)
    data = {}
    data['name'] = snap_name
    url = "https://{}/api/storage/volumes/{}/snapshots/{}".format(
                                storage, uuid,snap_uuid)

    try:
        resp = requests.get(
            url,
            headers=headers,
            verify=False
        )
    except requests.exceptions.HTTPError as e:
        print(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except Exception as e:
        print(e)
        sys.exit(1)

    url_res = resp.json()
    if 'error' in url_res:
        print(url_res)
        sys.exit(1)
    
    data = dict(url_res)

    t = PrettyTable(['Name', 'UUID','Volume','SVM', 'Creation time', 'Size'])

    t.add_row([
        data['name'],
        data['uuid'],
        data['volume']['name'],
        data['svm']['name'],
        data['create_time'],
        data['size'],

    ])
    print(t)

def update_snapshot(storage, svm, vol_name):
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    headers = res[1]

    snap_name = input('Enter the name of SNAPSHOT: ')
    snap_uuid = get_id_snapshot(storage, svm, vol_name,snap_name, headers)

    url = "https://{}/api/storage/volumes/{}/snapshots/{}".format(
                                storage, uuid,snap_uuid)

    try:
        resp = requests.patch(
            url,
            headers=headers,
            verify=False
        )
    except requests.exceptions.HTTPError as e:
        print(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except Exception as e:
        print(e)
        sys.exit(1)

    url_res = resp.json()
    if 'error' in url_res:
        print(url_res)
        sys.exit(1)
    
    data = dict(url_res)

    t = PrettyTable(['Name', 'UUID','Volume','SVM', 'Creation time', 'Size'])

    t.add_row([
        data['name'],
        data['uuid'],
        data['volume']['name'],
        data['svm']['name'],
        data['create_time'],
        data['size'],

    ])
    print(t)

def remove_snapshot(storage, svm, vol_name):
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    headers = res[1]
    
    snap_name = input('Enter the name of SNAPSHOT: ')
    snap_uuid = get_id_snapshot(storage, svm, vol_name,snap_name, headers)

    url_path = "https://{}/api/storage/volumes/" + \
        uuid + "/snapshots/" + snap_uuid
    url = url_path.format(storage)
    try:
        resp = requests.delete(
            url,
            headers=headers,
            verify=False
        )
    except requests.exceptions.HTTPError as e:
        print(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except Exception as e:
        print('ssss')
        print(e)
        sys.exit(1)

    url_res = resp.json()
    print(url_res)
    if 'error' in url_res:
        print(url_res)
        sys.exit(1)
    
    elif 'job' in url_res:
        job_status = url_res
        jobstat(job_status, headers, storage)

    else:
        print('-'*50)
        print(url_res)
        sys.exit(1)  

def main(args):
    storage = args['<STORAGE>']
    svm = args['<SVM>']
    vol_name = args['<VOLUME_NAME>']

    if args['--create']:
        create_snapshot(storage, svm, vol_name)
    if args['--details']:
        get_snapshot(storage, svm, vol_name)
    if args['--list']:
        list_snapshots(storage, svm, vol_name)
    if args['--remove']:
        remove_snapshot(storage, svm, vol_name)

if __name__ == '__main__':
    try:
        ARGS = get_args()

        main(ARGS)
    except KeyboardInterrupt:
        print('\nReceived Ctrl^C. Exiting....')

    except json.decoder.JSONDecodeError as e:
        print('\nError connecting to storage')
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print('\nError connecting to storage')
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print('\nError connecting to storage')
        sys.exit(1)
    except Exception:
        ETRACE = traceback.format_exc()
        print(ETRACE)