''' 
	classe configurazione
'''
import os 

class conf:
	
	db_password="1125"	
	db_user="virtmaster"
	db_name="virtbox"
	db_host="127.0.0.1"

		
	app_settings = {
		"base_address": "http://127.0.0.1",
		"project_name" : "virtBox",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
		"login_url": "/user/login/",
		"xsrf_cookies": True,
	}
		
