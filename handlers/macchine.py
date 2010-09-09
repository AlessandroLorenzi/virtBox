from handlers.homepage import BaseHandler
import libvirt
import xml.dom 
from xml.dom import minidom

global lvconn

print "== connecting to libvirt =="
lvconn = libvirt.open('qemu+ssh://alorenzi@darkstar.ricerca.dico.unimi.it/system')

''' Mostra una lista delle macchine '''
class Macchine(BaseHandler):
	def get(self):

		lista_macchine = list()
		for id in lvconn.listDefinedDomains():
			macchina={
				"state": "shutoff",
				"nome": id,
				"uuid": "",
			}
			lista_macchine.append(macchina)
			
		for id in lvconn.listDomainsID():
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
		self.render("home.html")


''' mostra i dettagli della macchina '''
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
	
