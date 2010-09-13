from handlers.homepage import BaseHandler
import hashlib
import time

class UserRegister(BaseHandler):
	def get(self):
		self.render("register_user.html", error = 0)
	def post(self):
		error = 0
		matricola=self.get_argument("matricola")
		cognome=self.get_argument("cognome")
		nome=self.get_argument("nome")
		passwd=self.get_argument("passwd")
		repasswd=self.get_argument("repasswd")
		OSha256 = hashlib.sha256()
		OSha256.update(matricola)
		OSha256.update(passwd)
		skey = OSha256.hexdigest()[:26]
		self.cursor.execute("SELECT count(matricola) as matricola_exist FROM utenti WHERE matricola = %s;" % matricola)
		self.database.commit()
		matricola_exist = self.cursor
		for (i) in  self.cursor:
			matricola_exist =  i[0]
		
		if passwd != repasswd:
			error = 1
		
		if matricola_exist != 0:
			print matricola_exist
			error = 2
		
		if error == 0:
			self.cursor.execute("INSERT INTO utenti (matricola, cognome, nome, password) VALUES (%s, '%s', '%s', '%s')" % ( matricola, cognome, nome, skey))
			self.database.commit()

			self.render("register_user_ok.html", matricola = matricola, nome = nome, cognome = cognome, passwd = passwd)
		else:
			self.render("register_user.html", error = error)
		
class UserLogin(BaseHandler):
	def get(self):
		self.render("login.html", error = 0)
	def post(self):
		error = 0
		matricola=self.get_argument("matricola")
		passwd=self.get_argument("passwd")
		OSha256 = hashlib.sha256()
		OSha256.update(matricola)
		OSha256.update(passwd)
		skey = OSha256.hexdigest()[:26]
		print skey
		self.cursor.execute("SELECT count(matricola) as matricola_exist FROM utenti WHERE matricola = %s AND password = '%s';" % (matricola, skey))
		self.database.commit()
		
		for (i) in  self.cursor:
			matricola_exist =  i[0]
		
		
		if matricola_exist == 0:
			error = 1
		
		if error == 0:
			self.set_secure_cookie("AuthUsername", str(matricola))
			self.render("login_ok.html")
		else:
			self.render("login.html", error = error)
	
class UserLogout(BaseHandler):
	def get(self):
		self.set_secure_cookie("AuthUsername", str(''))
		matricola = self.get_secure_cookie("AuthUsername")
		self.render("logout.html", error=0)
