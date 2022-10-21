import requests, base64
import json
import traceback
from docopt import docopt
from prettytable import PrettyTable
from utils import *
requests.packages.urllib3.disable_warnings()



def get_args():

	usage = """
	Usage:
		create_vol.py -s <STORAGE> -vm <SVM> -VN <VOLUME> <SIZE>
		create_vol.py --version
		create_vol.py -h | --help

	Options:
		-h --help            Show this message and exit
		-s <STORAGE>         ZFS appliance/storage name

	"""
	# version = '{} VER: {} REV: {}'.format(__program__, __version__, __revision__)
	# args = docopt(usage, version=version)
	args = docopt(usage)
	return args	


def create_vol(storage, vm, vol_name, size):

	headers = Headers()
	aggr_data={}
	aggr = requests.get('https://192.168.2.110/api/storage/aggregates',
					 verify=False, headers = headers)

	json1=aggr.json()
	aggr_data.update(json1)

	for i in aggr_data['records']:
		aggr_name = i['name']

	data = {
		"name" : vol_name,
		"size" : size,
		"svm" :
		{'name': vm}
		,
		"aggregates": [
		{'name': aggr_name}
		]
	}

	data_ = json.dumps(data)
	url = 'https://'+storage
	try:
		if vol_name.isalnum():
			t = PrettyTable()

			r = requests.post(url+'/api/storage/volumes', data = data_,
						 verify=False, headers = headers)


			res={}
			data1 = r.json()
			res.update(data1)


		
			if list(res.keys())[0] == 'error':
				print(res['error']['message'])

			else:
				try:
					resp={}
					d = r.json()
					url1 = 'https://'+storage+ d['job']['_links']['self']['href']
					req = requests.get(url1,verify=False, headers = headers)
					data1 = req.json()
					resp.update(data1)

					if resp['state'] == 'failure':
						t.field_names = [
						'SVM',
						'Aggr',
						'Status',
						'Details',
						]
						t.add_row(
						[vm,
						aggr_name,
						resp['state'],
						resp['message'],
						]
							)
						print(t)

					else:
						t.field_names = [
						'SVM',
						'Aggr',
						'Status',
						'Size',
						'Details',
						]

						t.add_row(
							[vm,
							aggr_name,
							resp['state'],
							size,
							resp['start_time'],
							]
							)
						print(t)
				
				except ValueError as err:
					print(err.args)
				except json.decoder.JSONDecodeError as err:
					print(err.args)
				except Exception as err:
					raise err


		else:
			print('SVM name is not valid!')

	except json.decoder.JSONDecodeError as err:
		print('Cant connect to the storage!')
		sys.exit(1)

	except requests.exceptions.HTTPError as err:
		print('Cant connect to the storage!')
		sys.exit(1)

	except requests.exceptions.RequestException as err:
		print('Cant connect to the storage!')
		sys.exit(1)
		
	except Exception as e:
		print(e) 
		sys.exit(1)

def main(args):
	storage = args['<STORAGE>']
	vm = args['<SVM>']
	vol_name = args['<VOLUME>']
	size = args['<SIZE>']


	create_vol(storage, vm, vol_name, size)


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