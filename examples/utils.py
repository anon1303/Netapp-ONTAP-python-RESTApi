from tkinter import EXCEPTION
import requests, base64
import json,time
import sys
from prettytable import PrettyTable
requests.packages.urllib3.disable_warnings()


def Headers():
	username = "admin"
	password = "netapp123"
	userpass = username + ':' + password
	encoded_u = base64.b64encode(userpass.encode()).decode()

	headers = {"Authorization" : "Basic %s" % encoded_u}

	return headers


        
def get_id_vol(svm, vol_name, storage):
    '''Get volume UUID'''
    header = Headers()
    url = "https://{}/api/storage/volumes?name={}&svm.name={}".format(
                                                    storage, vol_name, svm)
    vol = check_vol(storage, header, svm, vol_name)
    if vol == 0:
        print('Volume is not in the storage VM!')
        sys.exit(0)
    try:
        resp = requests.get(url, headers=header, verify=False)

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

    res = resp.json()
    if 'error' in res:
        print(res)
        print("ERROR! : "+res['error']['message'])
        sys.exit(1)

    vol = dict(res)
    for i in vol['records']:
        return i['uuid'],header

def jobstat(job_status, headers, storage):
    "check job status"
    t = PrettyTable()

    job_status_url = "https://{}/api/cluster/jobs/{}".format(
        storage, job_status['job']['uuid'])
    try:
        job_response = requests.get(
            job_status_url, headers=headers, verify=False)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)
    
    except Exception as e:
        print(e)
        sys.exit(1)

        
    job_status = job_response.json()

    if job_status['state'] == 'failure':
        t.field_names = [
                'UUID',
                'STATE',
                'Details',
                'CODE'
                ]

        t.add_row(
                [
                job_status['uuid'],
                job_status['state'],
                job_status['message'],
                job_status['code'],
                ]
            )
        print(t)
    elif job_status['state'] == 'running':
        t.field_names = [
                'UUID',
                'STATE',
                'Details',
                'CODE'
                ]

        t.add_row(
                [
                job_status['uuid'],
                job_status['state'],
                'success',
                '0',
                ]
            )
        print(t)


def check_vol(storage, header, svm, vol):
    url = "https://{}/api/storage/volumes/?svm.name={}".format(
        storage, svm)

    try:
        res = requests.get(
            url, headers=header, verify=False)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)
    
    except Exception as e:
        print(e)
        sys.exit(1)
    volume = dict(res.json())
    volumes = volume['records']
    vol_list = []
    for i in volumes:
        vol_list.append(i['name'])
        
    if vol in vol_list:
        return 1
    else:
        return 0

def get_id_snapshot(storage, svm, vol_name,snap_name, header):
    snap = check_snapshot(storage, svm, vol_name, snap_name)
    if snap == 0:
        print('Snapshot not found in the given volume')
        sys.exit(0)
    res = get_id_vol(svm, vol_name, storage)
    uuid = res[0]
    url = "https://{}/api/storage/volumes/{}/snapshots".format(
        storage, uuid)

    try:
        res = requests.get(
            url, headers=header, verify=False)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        print(e)
        sys.exit(1)
    
    except Exception as e:
        print(e)
        sys.exit(1)

    response = res.json()
    snapshot = dict(res.json())
    snapshots = snapshot['records']
    for i in snapshots:
        if i['name'] == snap_name:
            return i['uuid']


def check_snapshot(storage, svm, vol, snap_name):
    res = get_id_vol(svm, vol, storage)
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

    snap_list = []
    for i in snapshots:
        snap_list.append(i['name'])
        
    if snap_name in snap_list:
        return 1
    else:
        return 0

def get_size(size):
    try:
        tmp = int(size) * 1024 * 1024
        if tmp < 20971520:
            print('Size "10MB" ("10485760B") is too small.  Minimum size is "20MB" ("20971520B").')
            sys.exit(0)
        return tmp
    except ValueError:
        print('ERROR! size should be Integer only')
    except Exception as err:
        print(err)
    
def get_svmUUID(svm, storage):
    url = 'https://'+storage
    headers = Headers()

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

    svmdict = dict(r.json())

    if svmdict['num_records'] == 0 or len(svmdict['records']) == 0:
        print('No record Found for the svm named: ',svm)
        sys.exit(0)
    svmuuid = svmdict['records'][0]['uuid']

    return svmuuid


def check_svm(svm, storage):

    url = 'https://'+storage
    headers = Headers()

    vm_name = {}
    try:
        r = requests.get(url+'/api/svm/svms',
                            verify=False, headers = headers)
        data = r.json()
        vm_name.update(data)

        vm=[]

        for i in vm_name['records']:
            vm.append(i['name'])

        if svm in vm:
            message = {
                'message': 'The VM named '+svm+' is already running!',
                'code': 0 
            }
            return message

        else:
            message = {
                'message': svm+' Not found in the storage',
                'code': 1 
            }
            return message

    except requests.exceptions.ConnectionError as err:
        print('Cant connect to the storage!')
        sys.exit(1)

    except json.decoder.JSONDecodeError as err:
        print('Cant connect to the storage!')
        sys.exit(1)

    except requests.exceptions.HTTPError as err:
        print('Cant connect to the storage!')
        sys.exit(1)

    except requests.exceptions.RequestException as err:
        print('Cant connect to the storage!')
        sys.exit(1)
        
    except Exception as err:
        print(err)
        sys.exit(1)

def jobstat_(job_status, headers, storage):
    "check job status"
    if job_status['state'] == "failure":
        if job_status['code'] == 460770:
            print("SVM Already Exists")
        else:
            print("Operation failed due to :{}".format(job_status['message']))
    elif job_status['state'] == "success":
        print("Operation completed successfully.")
    else:
        job_status_url = "https://{}/api/cluster/jobs/{}".format(
            storage, job_status['uuid'])
        try:
            job_response = requests.get(
                job_status_url, headers=headers, verify=False)
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            print(err)
            sys.exit(1)
        job_status = job_response.json()
        time.sleep(2)
        jobstat_(job_status, headers, storage)