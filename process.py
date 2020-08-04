#written by mohlcyber 04.08.2020 v.0.3

import csv
import requests
import json
import time

from flask import Flask, render_template, request, jsonify

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxltieclient import TieClient

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

FILTERS = ['md5', 'sha1', 'sha256', 'hostname']

DXL_CERTS = '/path/to/dxlclient.config'
DXL_CONFIG = DxlClientConfig.create_dxl_config_from_file(DXL_CERTS)

EPO_IP = '1.1.1.1'
EPO_PORT = '8443'
EPO_USER = 'user'
EPO_PW = 'password'


class MAR():
	def __init__(self):
		self.url = 'https://{0}:{1}'.format(EPO_IP, EPO_PORT)
		self.headers = {'Content-Type': 'application/json'}
		self.verify = False

		self.auth = (EPO_USER, EPO_PW)

		self.queryId = None
		self.count = 0
		self.table_data = '<thead><tr><th>Hostname</th><th>IP</th><th>Status</th><th>Location</th><th>Hash</th><th>Type</th><th>Action</th></tr></thead>'

	def prep_payload(self, key, values):
		if key == 'hostname':
			# This will for hostname objects
			projections_container = []
			projections_dict = {'name': 'HostInfo'}
			projections_container.append(projections_dict)

			condition_container = {'or':[]}
			for host in values:
				condition_dict = {'and': []}
				condition_obj = {}
				condition_obj['name'] = 'HostInfo'
				condition_obj['output'] = 'hostname'
				condition_obj['op'] = 'EQUALS'
				condition_obj['value'] = host

				condition_dict['and'].append(condition_obj)
				condition_container['or'].append(condition_dict)

		else:
			# This will be for Hash objects
			projections_container = []

			projections_dict1 = {'name': 'HostInfo', 'outputs': ['hostname', 'ip_address']}
			projections_dict2 = {'name': 'Files', 'outputs': ['name', key, 'status', 'full_name']}

			projections_container.append(projections_dict1)
			projections_container.append(projections_dict2)

			condition_container = {'or': []}
			for hash in values:
				condition_dict = {'and': []}
				condition_obj = {}
				condition_obj['name'] = 'Files'
				condition_obj['output'] = key
				condition_obj['op'] = 'EQUALS'
				condition_obj['value'] = hash

				condition_dict['and'].append(condition_obj)
				condition_container['or'].append(condition_dict)


		payload = {}
		payload['projections'] = projections_container
		payload['condition'] = condition_container

		return payload

	def create_search(self, payload):
		res = requests.post(self.url + '/rest/mar/v1/searches/simple', headers=self.headers, auth=self.auth,
								data=json.dumps(payload), verify=self.verify)

		if res.status_code == 200:
			self.queryId = res.json()['id']

	def start_search(self):
		started = False
		res = requests.put(self.url + '/rest/mar/v1/searches/{}/start'.format(self.queryId), headers=self.headers,
						   auth=self.auth, verify=self.verify)

		if res.status_code == 200:
			started = True

		return started

	def status_search(self):
		done = False
		res = requests.get(self.url + '/rest/mar/v1/searches/{}/status'.format(self.queryId), headers=self.headers,
						   auth=self.auth, verify=self.verify)

		if res.status_code == 200:
			if res.json()['status'] == 'FINISHED':
				done = True

		return done

	def results(self):
		results = None
		res = requests.get(self.url + '/rest/mar/v1/searches/{}/results?$offset=0&$limit=1000'
						   .format(self.queryId), headers=self.headers, auth=self.auth, verify=self.verify)

		if res.status_code == 200:
			results = res.json()

		return results

	def results_parser(self, key, results):
		items = results['totalItems']
		print('STATUS: Found {} Systems.'.format(items))
		for item in results['items']:
			self.count += 1
			if key == 'hostname':
				hostname = item['output']['HostInfo|hostname']
				ip = item['output']['HostInfo|ip_address']
				status = item['output']['HostInfo|connection_status']
				platform = item['output']['HostInfo|platform']
				row_id = item['id']

				self.table_data += '<tbody><tr><td>{0}</td><td>{1}</td><td>{2}</td><td></td><td></td>\
				<td>{3}</td><td><button type="button" id="reaction-{4}" class="btn btn-danger btn-sm" \
				value="{5}|{6}" onclick="preq(this.id)">Quarantine</button></td></tr></tbody>'\
					.format(hostname, ip, status, platform, str(self.count), str(self.queryId), str(row_id))
			else:
				hostname = item['output']['HostInfo|hostname']
				ip = item['output']['HostInfo|ip_address']
				status = item['output']['Files|status']
				full_name = item['output']['Files|full_name']
				hash = item['output']['Files|{}'.format(key)]
				row_id = item['id']

				self.table_data += '<tbody><tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>\
				{4}</td><td>{5}</td><td><button type="button" id="reaction-{6}" class="btn btn-danger btn-sm" \
				value="{7}|{8}" onclick="preq(this.id)">Quarantine</button></td></tr></tbody>'\
					.format(hostname, ip, status, full_name, hash, key, str(self.count), str(self.queryId), str(row_id))

	def create_reaction(self, queryId, system_id, react_id):
		reaction_id = None
		payload = {
			"reactionId": react_id,
			"queryId": str(queryId),
			"resultIds": [str(system_id)],
			"reactionArguments": {}
		}

		res = requests.post(self.url + '/rest/mar/v1/reactionexecution', headers=self.headers, auth=self.auth,
							data=json.dumps(payload), verify=self.verify)

		if res.status_code == 200:
			reaction_id = res.json()['id']

		return reaction_id

	def start_reaction(self, reaction_id):
		started = False
		res = requests.put(self.url + '/rest/mar/v1/reactionexecution/{}/execute'.format(str(reaction_id)),
						   headers=self.headers, auth=self.auth, verify=self.verify)
		if res.status_code == 200:
			started = True
			print('REACTION: MAR reaction got executed successfully')

		return started

	def status_reaction(self, reaction_id):
		done = False
		res = requests.get(self.url + '/rest/mar/v1/reactionexecution/{}/status'.format(str(reaction_id)),
						   headers=self.headers, auth=self.auth, verify=self.verify)

		if res.status_code == 200:
			print('STATUS: MAR Reaction status is {}.'.format(res.json()['status']))
			if res.json()['status'] == 'FINISHED':
				done = True
		return done

	def main(self):
		print('STATUS: Query Systems via DXL. Please wait...')

		for key, values in OBJECTS.items():
			print('STATUS: Starting search for {}.'.format(key))
			payload = self.prep_payload(key, values)
			self.create_search(payload)
			if self.queryId is None:
				msg = 'ERROR: Could not create search.'
				return msg, None

			if self.start_search() is False:
				msg = 'ERROR: Could not start the search.'
				return msg, None

			while self.status_search() is False:
				print('STATUS: Waiting for 2 seconds to check again.')
				time.sleep(2)

			results = self.results()
			if results is not None:
				self.results_parser(key, results)

		return None, self.table_data


class TIE():
	def set_rep(self, hash, type, level, prov):
		with DxlClient(DXL_CONFIG) as client:
			client.connect()
			tie_client = TieClient(client)

			if prov == 'enterprise':
				tie_client.set_file_reputation(
					int(level), {
						type: hash
					},
					filename=hash,
					comment="Reputation Update from McAfee Bulk Importer"
				)
			elif prov == 'external':
				tie_client.set_external_file_reputation(
					int(level), {
						type: hash
					},
					filename=hash,
					comment="Reputation Update from McAfee Bulk Importer"
				)

	def main(self, level, prov):
		print('STATUS: Setting Reputations in TIE for {0}'.format(OBJECTS))
		for key, values in OBJECTS.items():
			for value in values:
				if key != 'hostname':
					self.set_rep(value, key, level, prov)

def filter_parser(filter_exist, headers, row):
	for filter in filter_exist:
		pos = headers.index(filter)
		if row[pos] != '':
			if filter not in OBJECTS:
				OBJECTS[filter] = []
			OBJECTS[filter].append(row[pos])
			return

def parser(filename):
	file = open('files/'+filename, 'r')
	readcsv = csv.reader(file, delimiter=',')
	headers = next(readcsv)
	filter_status = False
	filter_exist = []

	for fcheck in FILTERS:
		if fcheck in headers:
			filter_exist.append(fcheck)
			filter_status = True

	if filter_status is False:
		return 'Could not find the right filters in headers.'

	for row in readcsv:
		filter_parser(filter_exist, headers, row, )

	return None


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
	try:
		file = request.files['file']
		if file:

			global OBJECTS
			OBJECTS = {}

			file.save('files/'+file.filename)
			msg = parser(file.filename)

			if msg is not None:
				return jsonify({'error': msg})

			res = ''
			tie_msg = ''
			mar_msg = ''

			if request.form['tie'] == 'true':
				tie = TIE()
				tie.main(request.form['tie_rep'], request.form['tie_prov'])
				tie_msg = 'Successful set TIE Reputations.'

			if request.form['edr'] == 'true':
				mar = MAR()
				msg, res = mar.main()
				if msg is not None:
					return jsonify({'error': msg})

				mar_msg = 'Successful run EDR Query.'

			return jsonify({'msg': tie_msg + ' ' + mar_msg, 'res': str(res)})
		else:
			return jsonify({'error': 'Only CSV files are supported'})
	except Exception as error:
		return jsonify({'error': str(error)})


@app.route('/reaction', methods=['POST'])
def react():
	try:
		ids = request.form['ids']
		ids = ids.split('|')

		mar = MAR()
		reaction_id = mar.create_reaction(ids[0], ids[1], '22')
		if reaction_id is None:
			return jsonify({'error': 'Could not create new MAR reaction'})

		if mar.start_reaction(reaction_id) is False:
			return jsonify({'error': 'Could not start new MAR reaction'})

		while mar.status_reaction(reaction_id) is False:
			print('STATUS: Waiting for 2 seconds to check again.')
			time.sleep(2)

		return jsonify({'msg': 'Successfull quarantined system.'})

	except Exception as error:
		return jsonify({'error': str(error)})


@app.route('/unreact', methods=['POST'])
def unreact():
	try:
		ids = request.form['ids']
		ids = ids.split('|')

		mar = MAR()
		reaction_id = mar.create_reaction(ids[0], ids[1], '23')
		if reaction_id is None:
			return jsonify({'error': 'Could not create new MAR reaction'})

		if mar.start_reaction(reaction_id) is False:
			return jsonify({'error': 'Could not start new MAR reaction'})

		while mar.status_reaction(reaction_id) is False:
			print('STATUS: Waiting for 2 seconds to check again.')
			time.sleep(2)

		return jsonify({'msg': 'Successfull unquarantined system.'})

	except Exception as error:
		return jsonify({'error': str(error)})


if __name__ == '__main__':
	app.run(debug=True)