#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os, sys, re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import libvirt
import hashlib
import time
import psycopg2 as db

from tornado.options import define, options
''' handlers import '''
from handlers.homepage import BaseHandler, HomePage
from handlers.users import UserLogin, UserLogout
from handlers.templates import Template, TemplateAdd, TemplateDetails, TemplateDel
from handlers.aule import Aule, AulaAdd, AulaDetails, AulaDel
from handlers.macchine import Macchine, MacchinaAdd, MacchinaDetails, MacchinaDel, MacchinaRun, MacchinaShow, MacchinaForceOff



define( "port", default = 8888, help="run on the fiven port", type = int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", HomePage),
			(r"/user/login", UserLogin),
			(r"/user/logout", UserLogout),
			(r"/template/", Template),
			(r"/template/add/", TemplateAdd),
			(r"/template/(\w*)/", TemplateDetails),
			(r"/template/(\w*)/del/", TemplateDel),
			(r"/aule/", Aule),
			(r"/aula/add/", AulaAdd),
			(r"/aula/(\w*)/", AulaDetails),
			(r"/aula/(\w*)/del/", AulaDel),
			(r"/macchine/", Macchine),
			(r"/macchina/add/", MacchinaAdd),
			(r"/macchina/(\w*)/", MacchinaDetails),
			(r"/macchina/(\w*)/avvia/", MacchinaRun),
			(r"/macchina/(\w*)/visualizza/", MacchinaShow),
			(r"/macchina/(\w*)/force_off/", MacchinaForceOff),
			(r"/macchina/(\w*)/del/", MacchinaDel),
		]
		
		settings = {
			"base_address": "http://127.0.0.1",
			"project_name" : "virtBox",
			"static_path": os.path.join(os.path.dirname(__file__), "static"),
			"template_path": os.path.join(os.path.dirname(__file__), "templates"),
			"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
			"login_url": "/user/login",
			"xsrf_cookies": True,
		}
		
		tornado.web.Application.__init__(self, handlers, **settings)
		
		print "== connecting to database =="
		self.database = db.connect(database="alorenzi", user="alorenzi");
		self.cursor = self.database.cursor()
				

		
	def main(self):
		tornado.options.parse_command_line()
		http_server = tornado.httpserver.HTTPServer(Application())
		http_server.listen(options.port)
		print "== I'm ready baby ;) =="
		tornado.ioloop.IOLoop.instance().start()		
		
app = Application()
app.main()
