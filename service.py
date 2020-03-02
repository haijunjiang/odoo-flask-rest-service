from flask import Flask
import odoorpc
from flask.json import jsonify
from flask_httpauth import HTTPBasicAuth
from flask import request,abort,Response
from base64 import b64decode, b64encode
import json

app = Flask(__name__)
odoo = odoorpc.ODOO('localhost', port=8069)
# auth = HTTPBasicAuth()


# @auth.verify_password
# def verify_password(username, password):
# 	print("Verifyyyyy",username,verify_password)
# 	return False

# @app.route("/")
# def hello():
#     return "Root URL"

# @auth.login_required
@app.route("/api/payers")
def getPayers():
	auth_header = request.headers.get('Authorization')
	print("Argss:",request.args.to_dict())
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			# print(decode_res["username"] , decode_res['password'])
			
			# Check available databases
			# print(odoo.db.list())
			# Login
			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				# Current user
				user = odoo.env.user
				# print("User",user.name)            # name of the user connected
				# print("COmppp",user.company_id.name) # the name of its company
				Payer = odoo.env['payer_directory.payer']
				query = []
				for key,value in request.args.to_dict().iteritems():
					if key == "name":
						query.append((key,"ilike",value))
					elif key == "purpose_code":
						res_ids = []
						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("code","=",value)])
						print("purpose_code",purpose_ids)
						print("")
						print("")
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						query.append(("endpoints","in",endpoint_ids))
					elif key == "purpose":
						res_ids = []

						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("id","=",int(value))])
						print("purpose",purpose_ids)
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						
						query.append(("endpoints","in",endpoint_ids))
						
					else:
						query.append((key,"=",value))
				payer_ids = Payer.search(query)
				payers = []
				# print("payer_ids",)
				# print(payer_ids,)
				for payer_record in Payer.browse(payer_ids):
					print "payer_record",payer_record
					payer ={}
					payer['id']= payer_record.id
					payer['name']= payer_record.name

			    		payers.append(payer)
				# Simple 'raw' query
				# payers = payer_ids
				# print(payers)
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	return jsonify({'payers': payers})

# @auth.login_required
@app.route("/api/payer/<int:payer_id>")
def getPayerById(payer_id):
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			print(decode_res["username"] , decode_res['password'])
			
			# Check available databases
			print(odoo.db.list())
			# Login
			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				# Current user
				user = odoo.env.user
				# print("User",user.name)            # name of the user connected
				# print("COmppp",user.company_id.name) # the name of its company
				Payer = odoo.env['payer_directory.payer']
				payer_ids = Payer.search([("id","=",payer_id)])
				# print payer_ids
				payers = []
				print("payer_ids",)
				print(payer_ids,)
				if(not payer_ids):
					return jsonify({"Error":"Payer with given id not Found"}),404
				for payer_record in Payer.browse(payer_ids):
					print "payer_record",payer_record
					payer ={}
					payer['id']= payer_record.id
					payer['name']= payer_record.name
					payer['caqh_id']= payer_record.caqh_id
					payer["address"] = {
						
					}
			
					if(payer_record.street):
						payer["address"]["street"] =payer_record.street
					if(payer_record.street2):
						payer["address"]["street2"] =payer_record.street2
					if(payer_record.zip):
						payer["address"]["zip"] =payer_record.zip
					if(payer_record.city):
						payer["address"]["city"] =payer_record.city
					if(payer_record.state_id):
						payer["address"]["state"] =payer_record.state_id.name
					# if(payer_record.country_id):
					# 	payer["address"]["country"] =payer_record.country_id.name
					payer['oid']= payer_record.oid
					payer['caqh_id']= payer_record.caqh_id
					if payer_record.category:
						payer['category']={
							"id":payer_record.category.id,
							"name":payer_record.category.name
						}
					endpoints = []
					print(payer_record,payer_record.endpoints)
					for endpoint_record in payer_record.endpoints:
						print( "---",endpoint_record)
						endpoint = get_endpoint(endpoint_record)
						endpoints.append(endpoint)
					payer["endpoints"] = endpoints
					plans = []
					for plan_record in payer_record.plans:
						plan = get_plan(plan_record)
			    			plans.append(plan)
			    		payer['plans'] = plans
			    		contractors = []
			    		for contractor_record in payer_record.contractors:
			    			contractor = {}
			    			contractor["name"] = contractor_record['name'] 
			    			contractors.append(contractor)

			    		payer["contractors"] = contractors
			    		print("Payer:",payer)
			    		return jsonify(payer),200
			    		# payers.append(payer)
				# Simple 'raw' query
				# payers = payer_ids
				# print(payers)
			except Exception,e:
				print("Error -- payer!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	return jsonify({'payers': payers}),200

# @auth.login_required
@app.route("/api/plans")
def getPlans():
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			print(decode_res["username"] , decode_res['password'])
			
			# Check available databases
			print(odoo.db.list())
			# Login
			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				# Current user
				user = odoo.env.user
				# print("User",user.name)            # name of the user connected
				# print("COmppp",user.company_id.name) # the name of its company
				Plan = odoo.env['payer_directory.plan']
				query = []
				plan_ids = []
				for key,value in request.args.to_dict().iteritems():
					if key == "name":
						query.append((key,"ilike",value))
					elif key == "payer":
						query.append((key,"=",int(value)))
					elif key == "payer_caqh_id":
						Payer = odoo.env['payer_directory.payer']
						payer_ids = Payer.search([("caqh_id","=",value)])
						res_ids = []
						for payer in Payer.browse(payer_ids):
							res_ids = res_ids + payer.plans.ids
						query.append(("id","in",res_ids))
					elif key == "caqh_id":
						query.append((key,"=",str(value)))
					elif key == "purpose_code":
						res_ids = []
						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("code","=",value)])
						print("purpose_code",purpose_ids)
						print("")
						print("")
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						query.append(("endpoints","in",endpoint_ids))
					elif key == "purpose":
						res_ids = []

						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("id","=",int(value))])
						print("purpose",purpose_ids)
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						
						query.append(("endpoints","in",endpoint_ids))
						
					else:
						query.append((key,"=",value))
				print(query)
				if query:
					plan_ids = Plan.search(query)
				plans = []
				# print("payer_ids",)
				# print(payer_ids,)
				for plan_record in Plan.browse(plan_ids):
					plan = {}
					plan["name"] = plan_record.name
					plan["id"] = plan_record.id
					plans.append(plan)
				# Simple 'raw' query
				# payers = payer_ids
				print(plans)
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	return jsonify({'plans': plans})

# @auth.login_required
@app.route("/api/plan/<int:plan_id>")
def getPlanById(plan_id):
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				user = odoo.env.user

				Plan = odoo.env['payer_directory.plan']
				plan_ids = Plan.search([("id","=",plan_id)])
				if(not plan_ids):
					return jsonify({"Error":"Plan with given id not Found"}),404
				plans = []

				for plan_record in Plan.browse(plan_ids):
					plan = get_plan(plan_record)
		    		return jsonify(plan),200
				print(plans)
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	# return jsonify({'plans': plans})

# @auth.login_required
@app.route("/api/contractors")
def getContractors():
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			print(decode_res["username"] , decode_res['password'])
			
			# Check available databases
			print(odoo.db.list())
			# Login
			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				# Current user
				user = odoo.env.user
				# print("User",user.name)            # name of the user connected
				# print("COmppp",user.company_id.name) # the name of its company
				Contractor = odoo.env['payer_directory.contractor']
				query = []
				contractor_ids = []
				for key,value in request.args.to_dict().iteritems():
					if key == "name":
						query.append((key,"ilike",value))
					elif key == "payer":
						query.append((key,"=",int(value)))
					elif key == "payer_caqh_id":
						Payer = odoo.env['payer_directory.payer']
						payer_ids = Payer.search([("caqh_id","=",value)])
						for payer in Payer.browse(payer_ids):
							contractor_ids = contractor_ids + payer.contractors.ids
					elif key == "purpose_code":
						res_ids = []
						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("code","=",value)])
						print("purpose_code",purpose_ids)
						print("")
						print("")
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						query.append(("endpoints","in",endpoint_ids))
					elif key == "purpose":
						res_ids = []

						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids =Purpose.search([("id","=",int(value))])
						print("purpose",purpose_ids)
						Endpoint = odoo.env['payer_directory.endpoint']
						endpoint_ids = Endpoint.search([("purpose","in",purpose_ids)])
						# res_ids = Contractor.search([("endpoints","in",endpoint_ids)])
						
						query.append(("endpoints","in",endpoint_ids))
						
					else:
						query.append((key,"=",value))
				print(query)
				if(query):
					contractor_ids = Contractor.search(query)
				contractors = []
				# print("payer_ids",)
				# print(payer_ids,)
				for contractor_record in Contractor.browse(list(set(contractor_ids))):
					contractor = {}
					contractor["name"] = contractor_record.name
					contractor["id"] = contractor_record.id
					contractors.append(contractor)
				# Simple 'raw' query
				# payers = payer_ids
				print(contractors)
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	return jsonify({'contractors': contractors})

# @auth.login_required
@app.route("/api/contractor/<int:contractor_id>")
def getContractorById(contractor_id):
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				user = odoo.env.user
				Contractor = odoo.env['payer_directory.contractor']
				contractor_ids = Contractor.search([("id","=",contractor_id)])
				if(not contractor_ids):
					return jsonify({"Error":"Contractor with given id not Found"}),404
				contractors = []
				for contractor_record in Contractor.browse(contractor_ids):
					contractor = get_contractor(contractor_record)
		    		return jsonify(contractor),200
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403


# @auth.login_required
@app.route("/api/endpoints")
def getEndpoints():
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			print(decode_res["username"] , decode_res['password'])
			
			# Check available databases
			print(odoo.db.list())
			# Login
			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				# Current user
				user = odoo.env.user
				# print("User",user.name)            # name of the user connected
				# print("COmppp",user.company_id.name) # the name of its company
				Endpoint = odoo.env['payer_directory.endpoint']
				query = []
				for key,value in request.args.to_dict().iteritems():
					if key == "name":
						query.append((key,"ilike",value))
					elif key in ["payer","purpose"]:
						query.append((key,"=",int(value)))
					elif key == "payer_caqh_id":
						Payer = odoo.env['payer_directory.payer']
						payer_ids = Payer.search([("caqh_id","=",value)])
						print("payer_ids",payer_ids)
						res_ids = []
						for payer in Payer.browse(payer_ids):
							print(payer.name,payer.endpoints.ids)
							res_ids = res_ids+  payer.endpoints.ids
						query.append(("id","in",res_ids))

					elif key == "plan_caqh_id":
						Plan = odoo.env['payer_directory.plan']
						plan_ids = Plan.search([("caqh_id","=",value)])
						print("Plan ids",plan_ids)
						res_ids = []
						for plan in Plan.browse(plan_ids):
							res_ids = res_ids + plan.endpoints.ids
						query.append(("id","in",res_ids))
					elif key == "plan":
						Plan = odoo.env['payer_directory.plan']
						plan_ids = Plan.search([("id","=",int(value))])
						res_ids = []
						for plan in Plan.browse(plan_ids):
							res_ids = res_ids + plan.endpoints.ids
						query.append(("id","in",res_ids))
					elif key == "purpose_code":
						Purpose = odoo.env['payer_directory.endpoint.purpose']
						purpose_ids = Purpose.search([("code","=",value)])
						query.append(("purpose","in",purpose_ids))
					else:
						query.append((key,"=",value))
				print("QUeryyy:",query)

				endpoint_ids = Endpoint.search(query)
				endpoints = []
				# print("payer_ids",)
				# print(payer_ids,)
				for endpoint_record in Endpoint.browse(list(set(endpoint_ids))):
					endpoint = {}
					endpoint["id"] = endpoint_record.id
					endpoint["name"] = endpoint_record.name

					endpoints.append(endpoint)
				# Simple 'raw' query
				# payers = payer_ids
				print(endpoints)
				return  Response(json.dumps({'endpoints': endpoints}),headers={'Content-Type':'application/json'})

			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

	return jsonify({'endpoints': endpoints})
# @auth.login_required
@app.route("/api/pa_info",methods=['POST'])
def addPatient():
	print ("In get patient")
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				print("Trying")
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				print("Logged in")
				user = odoo.env.user
				PaInfo = odoo.env['epa_addons.pa_info']
				inputs = request.json
				if  'patient_id' in inputs:
					inputs['name'] = inputs['patient_id']
					del(inputs['patient_id'])
				pa_info_id = PaInfo.create(inputs)

				if (not pa_info_id):
					return jsonify({"Error": "Patient could not be created"}), 404

				pa_i = {}

				pa_i['result'] = pa_info_id
				print (pa_i)
				return jsonify(pa_i), 200
			except Exception, e:
				print("Error!", str(e))
				if (str(e).lower().find("access") > -1):
					return jsonify({"Error": "Access Denied"}), 403
				else:
					abort(500)

		else:
			return jsonify({"Error": "Invalid Credentials"}), 403
	else:
		return jsonify({"Error": "Invalid Authorization Header"}), 403

# @auth.login_required
@app.route("/api/pa_info/<patient_id>")
def getPatient(patient_id):
	print ("In get patient")
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				print("Trying")
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				print("Logged in")
				user = odoo.env.user
				PaInfo = odoo.env['epa_addons.pa_info']
				pa_info_ids = PaInfo.search([("name", "=", str(patient_id))])

				if (not pa_info_ids):
					return jsonify({"Error": "Patient with given id not Found"}), 404
				pa_info_set = []
				pa_i = {}
				print("Ok")
				for pa_info_record in PaInfo.browse(pa_info_ids):
					print ("Getting ",pa_info_record)
					painfo = get_painfo(pa_info_record)
					pa_info_set.append(painfo)
					print ("Record " ,painfo)
				pa_i['result'] = pa_info_set
				print (pa_i)
				return jsonify(pa_i), 200
			except Exception, e:
				print("Error!", str(e))
				if (str(e).lower().find("access") > -1):
					return jsonify({"Error": "Access Denied"}), 403
				else:
					abort(500)

		else:
			return jsonify({"Error": "Invalid Credentials"}), 403
	else:
		return jsonify({"Error": "Invalid Authorization Header"}), 403

# @auth.login_required
@app.route("/api/pa_info/<patient_id>/<app_context>",methods=['GET','DELETE'])
def getPatient(patient_id,app_context):
	print ("In get patient")
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				print("Trying")
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				print("Logged in")
				user = odoo.env.user
				PaInfo = odoo.env['epa_addons.pa_info']
				pa_info_ids = PaInfo.search([("name", "=", str(patient_id)),("app_context", "=", str(app_context))])

				if (not pa_info_ids):
					return jsonify({"Error": "Patient with given id not Found"}), 404
				pa_info_set = []
				pa_i = {}
				print("Ok")
				if request.method == 'DELETE':
					PaInfo.delete(pa_info_ids)
					return {"result":"DELETED"}
				for pa_info_record in PaInfo.browse(pa_info_ids):
					print ("Getting ",pa_info_record)
					painfo = get_painfo(pa_info_record)
					pa_info_set.append(painfo)
					print ("Record " ,painfo)
				pa_i['result'] = pa_info_set
				print (pa_i)
				return jsonify(pa_i), 200
			except Exception, e:
				print("Error!", str(e))
				if (str(e).lower().find("access") > -1):
					return jsonify({"Error": "Access Denied"}), 403
				else:
					abort(500)

		else:
			return jsonify({"Error": "Invalid Credentials"}), 403
	else:
		return jsonify({"Error": "Invalid Authorization Header"}), 403

# @auth.login_required
@app.route("/api/pa_info_cri/<patient_id>/<claim_response_id>",methods=['GET','DELETE'])
def getPatient_cri(patient_id,claim_response_id):
	print ("In get patient")
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				print("Trying")
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				print("Logged in")
				user = odoo.env.user
				PaInfo = odoo.env['epa_addons.pa_info']
				pa_info_ids = PaInfo.search([("name", "=", str(patient_id)),("claim_response_id", "=", str(claim_response_id))])

				if (not pa_info_ids):
					return jsonify({"Error": "Patient with given id not Found"}), 404
				pa_info_set = []
				pa_i = {}
				print("Ok")
				if request.method == 'DELETE':
					PaInfo.delete(pa_info_ids)
					return {"result":"DELETED"}
				for pa_info_record in PaInfo.browse(pa_info_ids):
					print ("Getting ",pa_info_record)
					painfo = get_painfo(pa_info_record)
					pa_info_set.append(painfo)
					print ("Record " ,painfo)
				pa_i['result'] = pa_info_set
				print (pa_i)
				return jsonify(pa_i), 200
			except Exception, e:
				print("Error!", str(e))
				if (str(e).lower().find("access") > -1):
					return jsonify({"Error": "Access Denied"}), 403
				else:
					abort(500)

		else:
			return jsonify({"Error": "Invalid Credentials"}), 403
	else:
		return jsonify({"Error": "Invalid Authorization Header"}), 403

# @auth.login_required
@app.route("/api/endpoint/<int:endpoint_id>")
def getEndpointById(endpoint_id):
	auth_header = request.headers.get('Authorization')
	if auth_header:
		decode_res = decode(auth_header)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:

			try:
				odoo.login('fhir', decode_res["username"], decode_res['password'])
				user = odoo.env.user
				Endpoint = odoo.env['payer_directory.endpoint']
				endpoint_ids = Endpoint.search([("id","=",endpoint_id)])
				if(not endpoint_ids):
					return jsonify({"Error":"Endpoint with given id not Found"}),404
				endpoints = []
				for endpoint_record in Endpoint.browse(endpoint_ids):
					endpoint = get_endpoint(endpoint_record)
		    		return jsonify(endpoint),200
			except Exception,e:
				print("Error!",str(e))
				if(str(e).lower().find("access") > -1):
					return jsonify({"Error":"Access Denied"}),403
				else:
					abort(500)
				
		else:
			return jsonify({"Error":"Invalid Credentials"}),403
	else:
		return jsonify({"Error":"Invalid Authorization Header"}),403

def get_painfo(record):
	painfo = {}
	painfo["patient_id"] = record.name
	if (record.date):
		painfo["date"] = record.date.strftime("%m/%d/%Y")

	if (record.app_context):
		painfo["app_context"] = record.app_context
	painfo["type"] = record.type
	painfo["claim_response_id"] = record.claim_response_id
	if (record.prior_auth_ref):
		painfo["prior_auth_ref"] = record.prior_auth_ref
	if (record.claim_response):
		painfo["claim_response"] = record.claim_response
	painfo["codes"] = record.codes
	return painfo


def get_plan(plan_record):
	plan = {}
	plan["name"] = plan_record.name
	plan["id"] = plan_record.id
	plan['caqh_id']= plan_record.caqh_id
	plan_endpoints=[]
	for endpoint_record in plan_record.endpoints:
		endpoint = get_endpoint(endpoint_record)
		plan_endpoints.append(endpoint)
		plan["endpoints"] = plan_endpoints
	return plan

def get_endpoint(endpoint_record):
	endpoint = {}
	endpoint['id']=endpoint_record.id
	endpoint['name'] = endpoint_record.name
	endpoint['caqh_id']= endpoint_record.caqh_id
	endpoint['authorize'] = endpoint_record.authorize
	endpoint['url'] = endpoint_record.url
	endpoint['auth_url'] = endpoint_record.auth_url
	endpoint['purpose'] = endpoint_record.purpose.name
	if(endpoint_record.payer):
		endpoint['payer'] = {'name':endpoint_record.payer.name,'id':endpoint_record.payer.id}
	endpoint['type_of_auth'] = endpoint_record.type_of_auth
	return endpoint

def get_contractor(contractor_record):
	contractor = {}
	contractor["name"] = contractor_record.name
	contractor["id"] = contractor_record.id
	contractor['caqh_id']= contractor_record.caqh_id
	contractor['jurisdiction']= contractor_record.jurisdiction
	contractor['oid']= contractor_record.oid
	
	contractor["address"] = {
		
	}

	if(contractor_record.street):
		contractor["address"]["street"] =contractor_record.street
	if(contractor_record.street2):
		contractor["address"]["street2"] =contractor_record.street2
	if(contractor_record.zip):
		contractor["address"]["zip"] =contractor_record.zip
	if(contractor_record.city):
		contractor["address"]["city"] =contractor_record.city
	if(contractor_record.state_id):
		contractor["address"]["state"] =contractor_record.state_id.name
	# if(contractor_record.country_id):
	# 	contractor["address"]["country"] =contractor_record.country_id.name
	contractor_endpoints=[]
	for endpoint_record in contractor_record.endpoints:
		endpoint = get_endpoint(endpoint_record)
		contractor_endpoints.append(endpoint)
		contractor["endpoints"] = contractor_endpoints


	return contractor

def decode(encoded_str):
    """Decode an encrypted HTTP basic authentication string. Returns a tuple of
    the form (username, password), and raises a DecodeError exception if
    nothing could be decoded.
    """
    print("In decodee")
    split = encoded_str.strip().split(' ')
    username = False
    password=False
    # If split is only one element, try to decode the username and password
    # directly.
    print(len(split))
    if len(split) == 1:
        try:
            username, password = b64decode(split[0]).decode().split(':', 1)
        except:
            jsonify({"Error":"Invalid Credentials"}),403

    # If there are only two elements, check the first and ensure it says
    # 'basic' so that we know we're about to decode the right thing. If not,
    # bail out.
    elif len(split) == 2:
    	print(split)
        if split[0].strip().lower() == 'basic':
            try:
                username, password = b64decode(split[1]).decode().split(':', 1)
                print username, password 
            except:
                jsonify({"Error":"Invalid Credentials"}),403
        else:
            return jsonify({"Error":"Invalid Authorization Header"}),403

    # If there are more than 2 elements, something crazy must be happening.
    # Bail.
    else:
        return jsonify({"Error":"Invalid Authorization Header"}),403
    return {"username":username,"password":password}

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=False)
