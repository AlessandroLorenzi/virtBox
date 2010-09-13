from handlers.homepage import BaseHandler
import libvirt
import xml.dom 
from xml.dom import minidom
import os
import commands

global lvconn

print "== connecting to libvirt == "
lvconn = libvirt.open('qemu+ssh://virtmaster@darkstar.ricerca.dico.unimi.it/system')

''' Mostra una lista delle macchine '''
class Macchine(BaseHandler):
	def get(self):
		
		matricola = self.get_secure_cookie("AuthUsername")

		self.cursor.execute("SELECT nome FROM macchine WHERE id_owner = %s;" % matricola)
		self.database.commit()
		
		nomi_macchine = list()
		for (i) in  self.cursor:
			nomi_macchine.append( i[0] )
		
		lista_macchine = list()
		
		for id in nomi_macchine:
			vm = lvconn.lookupByID(id)
			macchina={
				"state": "running",
				"nome": vm.name(),
				"uuid": vm.UUID(),
			}
			lista_macchine.append(macchina)
		
		self.render("lista_macchine.html", lista_macchine=lista_macchine)

''' '''
class MacchinaAdd(BaseHandler):
	def get(self):
		self.render("add_macchina.html", error = 0)
	def post(self):
		pass
		
		


class  MacchinaDetails(BaseHandler):
	def get(self, nome):
		
		vm = lvconn.lookupByName(nome)
		xml = vm.XMLDesc(0)
		xml = minidom.parseString(xml)
		
		
		
		memory = xml.getElementsByTagName('memory').item(0).firstChild.nodeValue
		memory = int(memory) /1024
		
		vcpu = xml.getElementsByTagName('vcpu').item(0).firstChild.nodeValue
		emulator = xml.getElementsByTagName('emulator').item(0).firstChild.nodeValue
		
		arch = xml.getElementsByTagName('os').item(0).getElementsByTagName('type').item(0).getAttribute('arch')
		
		vnc_port = xml.getElementsByTagName('graphics').item(0).getAttribute('port')

		devices = list()
		for disk in xml.getElementsByTagName('disk') :
			
			try:
				name = disk.getElementsByTagName('alias').item(0).getAttribute('name')
			except:
				name = "NoName"
				
			try:
				path = disk.getElementsByTagName('source').item(0).getAttribute('file')
			except:
				path = "-"
			
			try:
				dev = disk.getElementsByTagName('target').item(0).getAttribute('dev')
			except:
				path = "-"
			
			
			device = {
				'name': name,
				'path': path,
				'dev': dev,
			}
			devices.append(device)
		
		self.render("dettagli_macchina.html", nome=nome, memory = memory, vcpu = vcpu, arch = arch, devices= devices, emulator= emulator, vnc_port = vnc_port)
		
		

''' '''
class  MacchinaDel(BaseHandler):
	def get(self):
		self.render("home.html")


''' avvia una macchina '''
class  MacchinaRun(BaseHandler):
	def get(self, nome):
		try:
			vm = lvconn.lookupByName(nome)
			vm.resume()
			state = vm.info()[0]
		except:
			state = "0"
		self.render("avvia_macchina.html", state = state, nome = nome)

class  MacchinaShow(BaseHandler):
	def get(self):
		self.render("home.html")

class  MacchinaForceOff(BaseHandler):
	def get(self):
		self.render("home.html")

 
class  Dischi(BaseHandler):
	def get(self):
		self.cursor.execute("SELECT * FROM disks;")
		self.database.commit()
		disks = list()
		for disk in self.cursor:
			disk_list = list()
			disk_list.append(disk[0])
			disk_list.append(disk[1])
			disk_list.append(1 - os.path.exists('/home/alorenzi/virtBox/test/tmp/aria2c.' + str(disk[0]) +'.log'))
			disks.append(disk_list)
		self.render("dischi.html", lista_dischi = disks)

class  DiscoAdd(BaseHandler):
	def get(self):
		self.render("add_disco.html", error = 0)
		
	def post(self):
		error = 0
		nome = self.get_argument("nome")
		uri = self.get_argument("uri")
		dir = '/home/alorenzi/virtBox/test/'
		comando  = 'aria2c -D '
		comando += '-l "'+str(dir)+'/tmp/aria2c.' + str(nome) +'.log" '
		comando += '-d "'+str(dir)+'/libvirt/images/" '+str(uri)
		
		
		self.cursor.execute("SELECT * FROM disks WHERE name ='%s' OR uri = '%s'" % (nome, uri))
		self.database.commit()
		
		for i in self.cursor:
			error  = 1
		
		if error == 0:
			commands.getstatusoutput(comando)
			self.cursor.execute("INSERT INTO disks (name, uri) VALUES ('%s', '%s')" % ( nome,uri))
			self.database.commit()
			self.render("add_disco_ok.html")
		else:
			
			self.render("add_disco.html", error=error)
