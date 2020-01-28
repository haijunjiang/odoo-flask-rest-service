from flask import Flask
import odoorpc
from flask.json import jsonify
from flask_httpauth import HTTPBasicAuth
from flask import request,abort
from base64 import b64decode, b64encode





app = Flask(__name__)
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
	print auth_header
	if auth_header:
		print "ss"
		decode_res = decode(auth_header)
		print("decode res",decode_res)
		if "username" not in decode_res:
			return decode_res
		if decode_res["username"] and decode_res['password']:
			print(decode_res["username"] , decode_res['password'])
			odoo = odoorpc.ODOO('localhost', port=8069)
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
				payer_ids = Payer.search([])
				payers = []
				# print("payer_ids",)
				# print(payer_ids,)
				for payer_record in Payer.browse(payer_ids):
					print "payer_record",payer_record
					payer ={}
					payer['id']= payer_record.id
					payer['name']= payer_record.name
					endpoints = []
					print(payer_record,payer_record.endpoints)
					for endpoint_record in payer_record.endpoints:
						print( "---",endpoint_record)
						endpoint = {}
						endpoint['name'] = endpoint_record.name
						endpoint['authorize'] = endpoint_record.authorize
						endpoint['url'] = endpoint_record.url
						endpoint['auth_url'] = endpoint_record.auth_url
						endpoint['purpose'] = endpoint_record.purpose.name
						endpoint['type_of_auth'] = endpoint_record.type_of_auth
						endpoints.append(endpoint)
					payer["endpoints"] = endpoints
					plans = []
					for plan_record in payer_record.plans:
						plan = {}
						plan["name"] = plan_record.name
						plan_endpoints = []
						for endpoint_record in plan_record.endpoints:
							endpoint = {}
			    			endpoint['name'] = endpoint_record.name
			    			endpoint['authorize'] = endpoint_record.authorize
			    			endpoint['url'] = endpoint_record.url
			    			endpoint['auth_url'] = endpoint_record.auth_url
			    			endpoint['purpose'] = endpoint_record.purpose.name
			    			endpoint['type_of_auth'] = endpoint_record.type_of_auth
			    			plan_endpoints.append(endpoint)
			    			plan["endpoints"] = plan_endpoints
			    			plans.append(plan)
			    		payer['plans'] = plans
			    		contractors = []
			    		for contractor_record in payer_record.contractors:
			    			contractor = {}
			    			contractor["name"] = contractor_record['name'] 
			    			contractors.append(contractor)

			    		payer["contractors"] = contractors
			    		print("Payer:",payer)
			    		payers.append(payer)
				# Simple 'raw' query
				# payers = payer_ids
				print(payers)
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
