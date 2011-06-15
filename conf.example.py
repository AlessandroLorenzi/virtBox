''' 
	classe configurazione
'''
import os 

class conf:
	
	db_password=""	
	db_user=""
	db_name=""
	db_host="127.0.0.1"

		
	app_settings = {
		"base_address": "",
		"project_name" : "",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"cookie_secret": "CHANGEME",
		"login_url": "/user/login/",
		"xsrf_cookies": True,
	}
		
