#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os, sys, re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import libvirt
import time
import psycopg2 as db

from tornado.options import define, options
''' handlers import '''
from handlers.homepage import BaseHandler, HomePage
from handlers.User import UserList, User, GenericUser, UserRegister, UserLogin, UserLogout
from handlers.Guest import Guests, NewGuest, GuestDetails, GuestShow, GuestRun, GuestClone, GuestForceoff, GuestDel, GuestAddGroup, GuestDelGroup, setAsTemplate, GuestChmodUser, DefaultDisk, DeleteDisk
from handlers.Disk import DiskDownload, Disks
from conf import conf

define( "port", default = 8080, help="", type = int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", HomePage),
			(r"/users/", UserList),
			(r"/user/register/", UserRegister),
			(r"/user/login/", UserLogin),
			(r"/user/logout/", UserLogout),
			(r"/user/(\w*)/", User),
			(r"/user/", GenericUser),
			(r"/user/(\w*)/addgroup/", UserLogout),
			(r"/guests/", Guests),
			(r"/guest/new/", NewGuest),
			(r"/guest/clone/", GuestClone),
			(r"/guest/([\w%\-.]*)/", GuestDetails),
			(r"/guest/([\w%\-.]*)/run/", GuestRun),
			(r"/guest/([\w%\-.]*)/visualizza/", GuestShow),
			(r"/guest/([\w%\-.]*)/force_off/", GuestForceoff),
			(r"/guest/([\w%\-.]*)/del/", GuestDel),
			(r"/guest/([\w%\-.]*)/chmoduser/", GuestChmodUser),
			(r"/guest/([\w%\-.]*)/defaultdisk/([\w%\-]*)/", DefaultDisk),
			(r"/guest/([\w%\-.]*)/deletedisk/([\w%\-]*)/", DeleteDisk),
			(r"/disks/", Disks),
			(r"/disk/download/", DiskDownload),
		]
		
		settings = conf.app_settings
		
		tornado.web.Application.__init__(self, handlers, **settings)
		
		sys.stdout.write (" Connecting to database .... [WORK]")
		sys.stdout.flush()
		self.database = db.connect("dbname='%s' user='%s' host='%s' password='%s'  " % (conf.db_name, conf.db_user, conf.db_host, conf.db_password))
		self.cursor = self.database.cursor()
		sys.stdout.write ("\r Connecting to database .... [DONE] \n")
		
		

		
		
	def main(self):
		tornado.options.parse_command_line()
		http_server = tornado.httpserver.HTTPServer(Application())
		http_server.listen(options.port)
		print " {SYSTEM READY} "
		tornado.ioloop.IOLoop.instance().start()		
		
app = Application()
app.main()
