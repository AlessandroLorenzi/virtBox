from handlers.homepage import BaseHandler
import libvirt
import xml.dom 
from xml.dom import minidom
import os
import commands

global folder = '/serverones/'

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
		self.cursor.execute("SELECT * FROM disks;")
		self.database.commit()
		disks = list()
		for disk in self.cursor:
			disk_list = list()
			disk_list.append(disk[0])
			disk_list.append(disk[1])
			
			comando = "ps aux | grep '"+ disk[1] +"' | grep -v grep | head -n 1 | awk '{split ($0, a, \" \"); print a[2]}'"
			if  commands.getstatusoutput(comando) != '':
				disk_list.append(1)
			else:
				disk_list.append(0)
			disks.append(disk_list)
		
		self.render("add_macchina.html", error = 0, disks = disks)
	def post(self):
		folder = self.folder + '/libvirt/images/'

		domain_xml =  xml.dom.minidom.Document()

		domain = domain_xml.createElement('domain')
		domain.setAttribute('type', 'qemu')

		nome = domain_xml.createElement('nome')
		nome.appendChild(domain_xml.createTextNode( self.get_secure_cookie("AuthUsername")+'_'+self.get_argument("nome")))
		domain.appendChild(nome)

		memory = domain_xml.createElement('memory')
		memory.appendChild(domain_xml.createTextNode( int(self.get_argument("ram"))*1024 ))
		domain.appendChild(memory)

		currentMemory = domain_xml.createElement('currentMemory')
		currentMemory.appendChild(domain_xml.createTextNode( int(self.get_argument("ram"))*1024 ))
		domain.appendChild(currentMemory)

		vcpu = domain_xml.createElement('vcpu')
		vcpu.appendChild(domain_xml.createTextNode('1'))
		domain.appendChild(vcpu)

		os = domain_xml.createElement('os')
		ostmp = domain_xml.createElement('type')
		ostmp.setAttribute(self.get_argument("ram"), 'i686')
		ostmp.setAttribute('machine', 'pc')
		ostmp.appendChild(domain_xml.createTextNode('hvm'))
		os.appendChild(ostmp)


		ostmp = domain_xml.createElement('boot')
		ostmp.setAttribute('dev', 'cdrom')
		os.appendChild(ostmp)

		domain.appendChild(os)

		devices = domain_xml.createElement('devices')

		devicestmp =  domain_xml.createElement('emulator')
		devicestmp.appendChild(domain_xml.createTextNode('/usr/bin/kvm'))
		devices.appendChild(devicestmp)

		disk =  domain_xml.createElement('disk')
		disk.setAttribute('type', 'file')
		disk.setAttribute('device', 'cdrom')

		disktmp = domain_xml.createElement('source')
		disktmp.setAttribute('file', self.folder+'/'+self.get_argument("disk"))
		disk.appendChild(disktmp)

		disktmp = domain_xml.createElement('target')
		disktmp.setAttribute('dev', 'hdc')
		disk.appendChild(disktmp)

		disktmp = domain_xml.createElement('readonly')
		disk.appendChild(disktmp)

		devices.appendChild(disk)


		disk =  domain_xml.createElement('disk')
		disk.setAttribute('type', 'file')
		disk.setAttribute('device', 'disk')

		disktmp = domain_xml.createElement('source')

		commands.getstatusoutput('cp "'+self.folder+'/'+self.get_argument("disk")+'" "'self.folder + '/' + self.get_secure_cookie("AuthUsername")+'_'+self.get_argument("nome") +'.qcow"')
		disktmp.setAttribute('file',  self.folder + '/' + self.get_secure_cookie("AuthUsername")+'_'+self.get_argument("nome") +'.qcow')
		disk.appendChild(disktmp)

		disktmp = domain_xml.createElement('target')
		disktmp.setAttribute('dev', 'hda')
		disk.appendChild(disktmp)

		devices.appendChild(disk)

		interface = domain_xml.createElement('interface')
		interface.setAttribute('type', 'network')

		interfacetmp = domain_xml.createElement('source')
		interfacetmp.setAttribute('network', 'default')
		interface.appendChild(interfacetmp)

		devices.appendChild(interface)

		devicestmp = domain_xml.createElement('graphics')
		devicestmp.setAttribute('type', 'vnc')

		devices.appendChild(devicestmp)
		  
		domain.appendChild(devices)

		lvconn.createXML( domain.toprettyxml() )

		
		


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
			
			comando = "ps aux | grep '"+ disk[1] +"' | grep -v grep | head -n 1 | awk '{split ($0, a, \" \"); print a[2]}'"
			
			if  commands.getstatusoutput(comando) != '':
				disk_list.append(1)
			else:
				disk_list.append(0)
				
			disks.append(disk_list)
		self.render("dischi.html", lista_dischi = disks)

class  DiscoAdd(BaseHandler):
	def get(self):
		self.render("add_disco.html", error = 0)
		
	def post(self):
		error = 0
		
		uri = self.get_argument("uri")
		
		nome = self.get_argument("nome")
		
		aria2cdownfolder = self.folder+'/libvirt/images/'
		comando  = 'aria2c -D '
		comando += '-d "'+str(aria2cdownfolder)+'" '
		comando += str(uri)
		
		
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
