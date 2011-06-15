import tornado.httpserver
import libvirt

class BaseHandler(tornado.web.RequestHandler):
	@property
	def cursor(self):
		return self.application.cursor
	@property
	def database(self):
		return self.application.database
	

	
	def get_current_user(self):
		user_cookie= self.get_secure_cookie("61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o")
		if not user_cookie: return None
		return user_cookie

class HomePage(BaseHandler):
	def get(self):
		user = self.get_secure_cookie("AuthUsername")
		if not user:
			self.set_secure_cookie("AuthUsername", '')
			user=""
		self.render("home.html",user = user)

