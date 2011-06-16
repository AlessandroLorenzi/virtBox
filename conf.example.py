''' 
	classe configurazione
'''
import os 

class conf:
	
	db_password=""	
	db_user=""
	db_name=""
	db_host=""
	images_dir = ''		
	ssh_conn = ""
	libvirt_str = ''
		
	app_settings = {
		"base_address": "http://127.0.0.1",
		"project_name" : "virtBox",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"cookie_secret": "",
		"login_url": "/user/login/",
		"xsrf_cookies": True,
	}
