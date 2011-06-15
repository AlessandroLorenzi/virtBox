'''
TODO: avviare download con ssh!
'''

from handlers.homepage import BaseHandler
import commands

'''
	Avvia il download di un disk
'''
class DiskDownload (BaseHandler):
	def get(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.redirect('/')
			return
		self.render("DiskDownload.html", error = 0)
		
	def post(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.redirect('/')
			return
		error = 0
		
		uri = self.get_argument("uri")
		name = uri.split('/')[-1]

		aria2cdownfolder = '/serverones/libvirt/images/'
		cmd  = 'aria2c -D '
		cmd += '-d "%s" ' % str(aria2cdownfolder)
		cmd += str(uri)
		scmd  = 'ssh virtmaster@darkstar.ricerca.dico.unimi.it "%s"' % str(cmd)
		
		self.cursor.execute("SELECT * FROM disk WHERE name ='%s' OR uri = '%s'" % (name, uri))
		self.database.commit()
		for i in self.cursor:
			error  = 1
		
		if error == 0:
			commands.getstatusoutput(cmd)
			self.cursor.execute("INSERT INTO disk (name, uri) VALUES ('%s', '%s')" % ( name,uri))
			self.database.commit()
			self.render("DiskDownload_ok.html")
		else:
			
			self.render("DiskDownload.html", error=error)

		
'''
	Lista i CD/DVD di installer caricati su server
'''		
class Disks (BaseHandler):
	def get(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.redirect('/')
			return
		self.cursor.execute("SELECT * FROM disk;")
		self.database.commit()
		disks = list()
		for disk in self.cursor:
			disk_list = list()
			disk_list.append(disk[0])
			disk_list.append(disk[1])
			
			cmd = "ps aux | grep '%s' | grep aria2c | grep -v grep | wc -l" % disk[1]
			scmd  = 'ssh virtmaster@darkstar.ricerca.dico.unimi.it "%s"' % str(cmd)

			disk_list.append(commands.getstatusoutput(cmd)[1] )
			disks.append(disk_list)
		self.render("Disks.html", disks = disks)

