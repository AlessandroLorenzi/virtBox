from handlers.homepage import BaseHandler
import hashlib
import time

'''
	Visualizza informazioni sull'utente
'''
class User (BaseHandler):
	def get(self, username):
		try:
			usercursor = self.database.cursor()
			usercursor.execute("SELECT * FROM vuser WHERE username = '%s';" %(username))
			'''
				groupscursor = self.database.cursor()
				groupscursor.execute("SELECT usergroup FROM user2usergroup WHERE username = '%s';" %(username))
				
				egroupscursor = self.database.cursor()
				egroupscursor.execute("SELECT name FROM usergroup ")
			'''
		except:
			self.database.rollback()
		else:
			try: 
				self.database.commit()
				for (i) in usercursor:
					username = i[0]
					surname = i[1]
					name = i[2]
					
				groups= list()
				'''			
				for (i) in groupscursor:
					groups.append( i[0])

				'''			
				egroups= list()
				'''			
				for (i) in egroupscursor:
					egroups.append( i[0])
				'''				
			except:
				self.render("UserNotFound.html")
		self.render("User.html", username=username, surname=surname, name = name, groups=groups, egroups=egroups)	
'''
	reindirizza l'utente alla propria pagina
'''
class GenericUser (BaseHandler):
	def get(self):
		username=self.get_secure_cookie("AuthUsername")
		self.redirect('/user/%s/'%username)
		

'''
	Stampa la lista degli utenti
'''
class UserList (BaseHandler):
	def get(self):
		users= list()
		try:
			self.cursor.execute("SELECT username FROM vuser;")
		except:
			self.database.rollback()
		else:
			self.database.commit()
			for (user) in self.cursor:
					users.append(str(user[0]))
		self.render("UserList.html", users=users)
		
'''
	registrazione di un nuovo utente
'''
class UserRegister (BaseHandler):
	def get(self):
		self.render("RegisterUser.html", error = 0)
	def post(self):
		error = 0
		username=self.get_argument("username")
		surname=self.get_argument("surname")
		name=self.get_argument("name")
		passwd=self.get_argument("passwd")
		repasswd=self.get_argument("repasswd")
		
		if passwd != repasswd:
			self.render("RegisterUser.html", error = 1)
			return
		
		self.cursor.execute("SELECT RegisterUser('%s', '%s', '%s', '%s')" % ( username, surname, name, passwd))
		self.database.commit()
		for (i) in  self.cursor:
			username_exist =  i[0]

		if username_exist>0:
			self.render("RegisterUser.html", error = 2)
			return			
		
			
		self.render("RegisterUser_ok.html", username = username, name = name, surname = surname, passwd = passwd)
		
		
'''
	login dell'utente
'''
class UserLogi_old (BaseHandler):
	def get(self):
		self.render("Login.html", error = 0)
	def post(self):
		error = 0
		username=self.get_argument("username")
		passwd=self.get_argument("passwd")
		self.cursor.execute("SELECT VerifyPassword ('%s','%s');" % (username, passwd))
		self.database.commit()
		
		for (i) in  self.cursor:
			verified =  i[0]
		
		if  verified:
			print ("%s %s " %(username, passwd))
			self.set_secure_cookie("AuthUsername", str(username))
			self.render("Login_ok.html")
		else:
			self.render("Login.html", error = 1)
		
class UserLogin (BaseHandler):
	def update_database(self, username, passwd):
		
		self.cursor.execute("SELECT RegisterUser('%s', '%s', '%s', '%s')" % ( username, "", "", passwd))
		self.database.commit()

		return		

	def get(self):
		self.render("Login.html", error = 0)
	def post(self):
		from radius import RADIUS
		error = 0
		username=self.get_argument("username")
		passwd=self.get_argument("passwd")
		
		host = b"ghost.dsi.unimi.it"
		port = 1812
		secret = b"d4rkst4r"

		r = RADIUS(secret,host,port)

		if  r.authenticate(str("%s@silab.dsi.unimi.it" %username),str(passwd)):
			self.set_secure_cookie("AuthUsername", str(username))
			self.update_database(username, passwd)
			self.render("Login_ok.html")
		else:
			self.render("Login.html", error = 1)
	
		
			
			
'''
	logout dell'utente
'''
class UserLogout (BaseHandler):
	def get(self):
		self.set_secure_cookie("AuthUsername", str(''))
		matricola = self.get_secure_cookie("AuthUsername")
		self.render("Logout.html", error=0)

'''
	Inserisce l'utente nel gruppo
'''
class UserAddGroup (BaseHandler):
	def get(self):
		pass
		
	def post(self,username):
		try:
			group = self.get_argument("group")
			self.cursor.execute("INSERT INTO user2usergroup VALUES('%s', '%s')"%(username,group))
		except:
			self.database.rollback()
		else:
			self.database.commit()

		self.redirect('/user/%s/'%username)


'''
	Rimuove l'utente dal gruppo
'''
class UserDelGroup (BaseHandler):
	def get(self):
		pass
	
	def post(self):
		pass
