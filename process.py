#written by mohlcyber 11.01.2020 v.0.1

import os
import csv

from flask import Flask, render_template, request, jsonify

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlmarclient import MarClient
from dxltieclient import TieClient

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['csv'])
PATH = "/Users/mohl/Desktop/test/"
HASHES = {}

DXL_CERTS = '/Users/mohl/Desktop/dxl_certs/new/dxlclient.config'
DXL_CONFIG = DxlClientConfig.create_dxl_config_from_file(DXL_CERTS)

class EDR():

	def __init__(self):
		self.table_data = '<thead><tr><th>Hostname</th><th>IP</th><th>Status</th><th>Location</th><th>Hash</th><th>Type</th></tr></thead>'

	def search(self, hash, type):
		with DxlClient(DXL_CONFIG) as client:

			client.connect()
			marclient = MarClient(client)

			results_context = \
				marclient.search(
					projections=[{
						"name": "HostInfo",
						"outputs": ["hostname", "ip_address"]
					}, {
						"name": "Files",
						"outputs": ["name", type, "status", "full_name"]
					}],
					conditions={
						"or": [{
							"and": [{
								"name": "Files",
								"output": type,
								"op": "EQUALS",
								"value": hash
							}]
						}]
					}
				)

			if results_context.has_results:
				results = results_context.get_results()

				total = results['totalItems']
				print('SUCCESS: Found {0} Host(s) with hash {1}.'.format(str(total), hash))

				for item in results['items']:
					hostname = item['output']['HostInfo|hostname']
					ip = item['output']['HostInfo|ip_address']
					status = item['output']['Files|status']
					full_name = item['output']['Files|full_name']

					self.table_data += '<tbody><tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr></tbody>'\
						.format(hostname, ip, status, full_name, hash, type)

				return self.table_data
			else:
				return None

	def main(self):
		print('STATUS: Query Systems via DXL. Please wait...')
		for key, values in HASHES.items():
			for value in values:
				self.search(value, key)

		return self.table_data


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
					comment="Reputation Update from McAfee CSV Importer"
				)
			elif prov == 'external':
				tie_client.set_external_file_reputation(
					int(level), {
						type: hash
					},
					filename=hash,
					comment="Reputation Update from McAfee CSV Importer"
				)

	def main(self, level, prov):
		print('STATUS: Setting Reputations in TIE for {0}'.format(HASHES))
		for key, values in HASHES.items():
			for value in values:
				self.set_rep(value, key, level, prov)


def parser(filename):
	file = open(PATH + filename, 'r')
	readcsv = csv.reader(file, delimiter=',')
	headers = next(readcsv)
	md5_pos = headers.index('md5')
	sha1_pos = headers.index('sha1')
	sha256_pos = headers.index('sha256')

	md5s = []
	sha1s = []
	sha256s = []

	for row in readcsv:
		if row[md5_pos] != '':
			md5s.append(row[md5_pos])
			HASHES['md5'] = md5s
		elif row[sha1_pos] != '':
			sha1s.append(row[sha1_pos])
			HASHES['sha1'] = sha1s
		elif row[sha256_pos] != '':
			sha256s.append(row[sha256_pos])
			HASHES['sha256'] = sha256s

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
	try:
		file = request.files['file']
		if file.filename == '':
			return jsonify({'error': 'No file selected for uploading'})
		if file and allowed_file(file.filename):
			file.save(os.path.join(PATH, file.filename))
			parser(file.filename)
			res = ''
			tie_msg = ''
			edr_msg = ''

			if request.form['tie'] == 'true':
				tie = TIE()
				tie.main(request.form['tie_rep'], request.form['tie_prov'])
				tie_msg = 'Successful set TIE Reputations.'

			if request.form['edr'] == 'true':
				edr = EDR()
				res = edr.main()
				edr_msg = 'Successful run EDR Query.'

			return jsonify({'msg': tie_msg + ' ' + edr_msg, 'res': str(res)})
		else:
			return jsonify({'error': 'Only CSV files are supported'})
	except Exception as error:
		return jsonify({'error': str(error)})

if __name__ == '__main__':
	app.run(debug=True)