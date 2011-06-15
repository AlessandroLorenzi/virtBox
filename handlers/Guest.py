from handlers.homepage import BaseHandler
import libvirt, os, sys, commands, urllib, random, xml
from xml.dom import minidom
from handlers.Permission import Permission

global folder
folder = '/serverones/'


global lvconn

sys.stdout.write (" Connecting to libvirtd .... [WORK]")
sys.stdout.flush()
lvconn = libvirt.open('qemu+ssh://virtmaster@darkstar.ricerca.dico.unimi.it/system')
sys.stdout.write ("\r Connecting to libvirtd .... [DONE]\n")

'''
	Stampa la lista delle macchine installate su cui l'utente
	loggato gode dei permessi.
'''
class Guests (BaseHandler):
	def get(self):
		username = self.get_secure_cookie("AuthUsername")
		if username == '':
			self.render("NotPermitted.html")
			return

		self.cursor.execute("SELECT guest.name FROM guest JOIN acl_g2u ON guest.name = acl_g2u.guest JOIN vuser ON acl_g2u.username = vuser.username WHERE vuser.username = '%s';" % str(username))
		self.database.commit()
		
		guests = list()
		for (i) in  self.cursor:
			guests.append( str(i[0]) )
		
		guest_list = list()
		
		for id in guests:
			try:
				vm = lvconn.lookupByName(str(id))
				state = vm.info()[0]
				guest={
					"state": state,
					"name": vm.name(),
					"uuid": vm.UUID(),
				}
				guest_list.append(guest)
			except:
				print("Inconsistenza tra libvirt e database")
		
		self.render("GuestList.html", guests=guest_list)

'''
	Visualizza una schermata con i dettagli della guest.
'''
class GuestDetails (BaseHandler):
	def get(self, name):
		gname = urllib.unquote(name)
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
			
		try:	
			vm = lvconn.lookupByName(name)
		except:
			self.redirect('/guests/')
		xml = vm.XMLDesc(1)
		xml = minidom.parseString(xml)
		
		active = vm.isActive()	
		
		memory = xml.getElementsByTagName('memory').item(0).firstChild.nodeValue
		memory = int(memory) /1024
		
		vcpu = xml.getElementsByTagName('vcpu').item(0).firstChild.nodeValue
		emulator = xml.getElementsByTagName('emulator').item(0).firstChild.nodeValue
		
		arch = xml.getElementsByTagName('os').item(0).getElementsByTagName('type').item(0).getAttribute('arch')
		
		vnc_port = xml.getElementsByTagName('graphics').item(0).getAttribute('port')
		vnc_passwd = xml.getElementsByTagName('graphics').item(0).getAttribute('passwd')

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
			
			try:
				typed = disk.getAttribute('device')
			except:
				typed = "-"
			
			device = {
				'name': name,
				'path': path,
				'dev': dev,
				'typed': typed,
			}
			devices.append(device)

		permissions=list()

		try:
			self.cursor.execute("SELECT username, permissions FROM  acl_g2u WHERE guest = '%s';" % gname)
			tmpcursor = self.database.cursor()
			tmpcursor.execute("SELECT username FROM vuser ;" )
		except:
			self.database.rollback()
			print "ERROR"
		else:
			self.database.commit()
			for perm in  self.cursor:
				''' <madness > '''
				permbyte = '{0:08b}'.format(perm[1])
				''' </madness> '''
				permissions.append({
					'name': perm[0],
					'show': permbyte[7],
					'run': permbyte[6],
					'delete': permbyte[5] ,
					'clone':permbyte[4] ,
					'chmod': permbyte[3] 
				})
			users = list()
			for  user in tmpcursor:
				users.append(user[0])

		self.render("GuestDetails.html", name=gname, memory = memory, vcpu = vcpu, arch = arch, devices= devices, emulator= emulator, vnc_port = vnc_port, vnc_passwd=vnc_passwd, active=active, permissions=permissions, users=users)


'''
	mostra un applet java con vnc con impostato l'indirizzo e porta
	della guest virtuale
'''	
class GuestShow (BaseHandler):
	def get(self):
		pass
	
	def post(self):
		pass
		
'''
	Instanzia una nuova guest pulita
'''
class NewGuest (BaseHandler):
	def get(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		
		self.cursor.execute("SELECT * FROM disk;")
		self.database.commit()
		disks = list()
		for disk in self.cursor:
			disk_list = list()
			disk_list.append(disk[0])
			disk_list.append(disk[1])
			
			cmd = "ps aux | grep '%s' | grep aria2c | grep -v grep | wc -l" %disk[1]
			scmd = 'ssh darkstar.ricerca.dico.unimi.it "%s"' % str(cmd)
			if  int(commands.getstatusoutput(cmd)[1]) == 0:
				disk_list.append(1)
			else:
				disk_list.append(0)
			disks.append(disk_list)

		self.cursor.execute("SELECT * FROM hdd_image;")
		self.database.commit()
		hdd_images = list()
		for hdd_image in self.cursor:
			hdd_images.append(hdd_image)	

		self.render("NewGuest.html", error = 0, disks = disks, hdd_images = hdd_images)
		
	def post(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
        
		guest_name = self.get_secure_cookie("AuthUsername")+"_"+self.get_argument("name")
		folder = '/serverones/libvirt/images/'


		domain_xml =  xml.dom.minidom.Document()

		domain = domain_xml.createElement('domain')
		if self.get_argument("arch") == "i686":
			domain.setAttribute('type', 'kvm')
		else:
			domain.setAttribute('type', 'qemu')

		name = domain_xml.createElement('name')
		name.appendChild(domain_xml.createTextNode(guest_name ))
		domain.appendChild(name)

		memory = domain_xml.createElement('memory')
		memory.appendChild(domain_xml.createTextNode(str( int(self.get_argument("ram"))*1024 )))
		domain.appendChild(memory)

		currentMemory = domain_xml.createElement('currentMemory')
		currentMemory.appendChild(domain_xml.createTextNode( str( int(self.get_argument("ram")))))
		
		os = domain_xml.createElement('os')
		
		ostmp = domain_xml.createElement('type')
		ostmp.setAttribute('arch', self.get_argument("arch"))
		ostmp.setAttribute('machine', 'pc')
		
		if self.get_argument("arch") == "i686":
			ostmp.appendChild(domain_xml.createTextNode('hvm'))
		else:
			ostmp.appendChild(domain_xml.createTextNode('linux'))
			
		os.appendChild(ostmp)


		ostmp = domain_xml.createElement('boot')

		if  self.get_argument("hdd_image") == '0':
			ostmp.setAttribute('dev', 'cdrom')
		else:
			ostmp.setAttribute('dev', 'hd')
		os.appendChild(ostmp)

		domain.appendChild(os)

		devices = domain_xml.createElement('devices')

		vnc = domain_xml.createElement('graphics')
		vnc.setAttribute('passwd', str(random.randint(1111,9999)))
		vnc.setAttribute('autoport', 'yes')
		vnc.setAttribute('type', 'vnc')
		devices.appendChild(vnc)

		devicestmp =  domain_xml.createElement('emulator')
		devicestmp.appendChild(domain_xml.createTextNode('/usr/bin/kvm'))
		devices.appendChild(devicestmp)

		if  self.get_argument("hdd_image") == '0':
			disk =  domain_xml.createElement('disk')
			disk.setAttribute('type', 'file')
			disk.setAttribute('device', 'cdrom')

			disktmp = domain_xml.createElement('source')
			disktmp.setAttribute('file', '%s/%s' % (folder, self.get_argument("cdrom")))
			disk.appendChild(disktmp)

			disktmp = domain_xml.createElement('target')
			disktmp.setAttribute('dev', 'hdc')
			disk.appendChild(disktmp)

			disktmp = domain_xml.createElement('readonly')
			disk.appendChild(disktmp)

			devices.appendChild(disk)
		else:
			pass

		disk =  domain_xml.createElement('disk')
		disk.setAttribute('type' , 'file')
		disk.setAttribute('device' , 'disk')

		target = domain_xml.createElement('target')
		target.setAttribute('dev', 'hda')
		target.setAttribute('bus', 'ide')
		disk.appendChild(target)

		driver = domain_xml.createElement('driver')
		driver.setAttribute('name', 'qemu')
		driver.setAttribute('type', 'qcow2')
		disk.appendChild(driver)


		source = domain_xml.createElement('source')
		source.setAttribute('file',  "%s/%s.qcow" % (folder, guest_name))
		disk.appendChild(source)

		#qemuimg = ('ssh darkstar.ricerca.dico.unimi.it \'/usr/bin/qemu-img create -f qcow2 "%s/%s.qcow" \' %s' % 
		if  self.get_argument("hdd_image") == '0':
			cmd = ('/usr/bin/qemu-img create -f qcow2 "%s/%s.qcow" %s' % 
				(folder, guest_name, self.get_argument("disk")))
		else:
			cmd = ('cp %s/%s %s/%s.qcow' % 
				(folder, self.get_argument("hdd_image"), folder, guest_name ))
		print commands.getstatusoutput(cmd)
		
		devices.appendChild(disk)


		interface = domain_xml.createElement('interface')
		interface.setAttribute('type', 'network')

		interfacetmp = domain_xml.createElement('source')
		interfacetmp.setAttribute('network', 'default')
		interface.appendChild(interfacetmp)
		
		interfacetmp=  domain_xml.createElement('model')
		interfacetmp.setAttribute('type', 'e1000')
		interface.appendChild(interfacetmp)

		devices.appendChild(interface)
		  
		domain.appendChild(devices)
	
		try: 
			new = lvconn.defineXML( domain.toxml())
			new.create()
			self.cursor.execute("SELECT CreateGuest('%s', '%s')" %
					(guest_name, self.get_secure_cookie("AuthUsername")))
		except:
			print("ERROR: SELECT CreateGuest('%s', '%s')" %
                   (guest_name, self.get_secure_cookie("AuthUsername")))
			self.database.rollback()
			self.cursor.execute("SELECT * FROM disk;")
			self.database.commit()
			disks = list()
			for disk in self.cursor:
				disk_list = list()
				disk_list.append(disk[0])
				disk_list.append(disk[1])
				
				comando = "ps aux | grep '%s' | grep aria2c | grep -v grep | wc -l" %disk[1]
				if  int(commands.getstatusoutput(comando)[1]) == 0:
					disk_list.append(1)
				else:
					disk_list.append(0)
				disks.append(disk_list)
			self.render("NewGuest.html", error = 1, disks = disks, hdd_images = list())
		else:
			self.database.commit()
			self.redirect('/guests/')

'''
	Avvia una guest spenta.
'''
		
class GuestRun (BaseHandler):
	def get(self, name):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		name=urllib.unquote(name)
		p= Permission(self.database)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), name, 6)  == 0:
			self.render("NotPermitted.html")
			return
		try:
			vm = lvconn.lookupByName(name)
			vm.create()
			state = vm.info()[0]
		except:
			state = "0"
		self.redirect('/guest/'+name+'/')
'''
	Cambia il disco di default
'''
class DefaultDisk (BaseHandler):
	def get(self, name, disk):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		name=urllib.unquote(name)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), name, 6)  == 0:
			self.render("NotPermitted.html")
			return
		try:
			vm = lvconn.lookupByName(name)
			xml = vm.XMLDesc(1)
			xml = minidom.parseString(xml)
			os = xml.getElementsByTagName("os")
			os= os[0]
			devices = xml.getElementsByTagName("devices")
			devices= devices[0]
			#print(devices.toprettyxml())
			boot = xml.getElementsByTagName("boot")
			for tmpboot in boot:
				os.removeChild(tmpboot)
			boot = xml.createElement("boot")
			if disk=="disk":
				disk="hd"
			boot.setAttribute("dev", disk)
			os.appendChild(boot)
			if vm.isActive():
				vm.destroy()
			vm.undefine()
			new = lvconn.defineXML( xml.toxml())
			new.create()
		except:
			print("err")
			pass
		self.redirect('/guest/'+name+'/')
'''
	elimina il disco	
'''
class DeleteDisk (BaseHandler):
	def get(self, name, disk):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		name=urllib.unquote(name)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), name, 6)  == 0:
			self.render("NotPermitted.html")
			return
		try:
			vm = lvconn.lookupByName(name)
			xml = vm.XMLDesc(1)
			xml = minidom.parseString(xml)
			os = xml.getElementsByTagName("os")
			os= os[0]
			disks= xml.getElementsByTagName("disk")
			for dsk in disks:
				if dsk.getAttribute('device')==disk:
					disks.removeChild(dsk)
					print dsk.getAttribute('device')
			
			if vm.isActive():
				vm.destroy()
			vm.undefine()
			new = lvconn.defineXML( xml.toxml())
			new.create()
		except:
			print("err")
			pass
		self.redirect('/guest/'+name+'/')
		
		

'''
	Effettua il clone di una guest
'''
class GuestClone (BaseHandler):
	def post(self):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		
		original= self.get_argument("original")
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), original, 4)  == 0:
			self.redirect('/')
			return
		new= self.get_secure_cookie("AuthUsername")+'_'+str(self.get_argument("new"))
		diskname='/serverones/libvirt/images/'+new+'.qcow'
		cmd = "virt-clone -o %s -n %s -f %s --connect=qemu+ssh://127.0.0.1/system " % (original, new, diskname)
		scmd = 'ssh virtmaster@darkstar.ricerca.dico.unimi.it "%s" ' % cmd 
		try:
			commands.getstatusoutput(cmd)
			self.cursor.execute("SELECT CreateGuest('%s', '%s')" %
					(new, self.get_secure_cookie("AuthUsername")))
		except: 
			self.database.rollback()
		else:
			self.cursor.execute("SELECT CreateGuest('%s', '%s')" %
					(new, self.get_secure_cookie("AuthUsername")))
			self.database.commit()
			
		self.redirect('/guest/%s/' % str(new))
		
'''
	Forza lo spegnimento della guest
'''
class GuestForceoff (BaseHandler):
	def get(self, name):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		name=urllib.unquote(name)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), name, 3)  == 0:
			self.render("NotPermitted.html")
			return
		
		guest = lvconn.lookupByName(name)
		guest.destroy()
		self.redirect("/guest/"+name+"/")

'''
	Elimina la guest
'''	
class GuestDel (BaseHandler):
	def get(self, name):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		name=urllib.unquote(name)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), name, 5)  == 0:
			self.render("NotPermitted.html")
			return
		try:

			vm = lvconn.lookupByName(name)
			if vm.isActive():
				vm.destroy()
			vm.undefine()
			self.cursor.execute("DELETE FROM guest WHERE name = '%s'; " %  str(name))
		except:
			self.database.rollback()
		else:
			self.database.commit()
			folder = '/serverones/libvirt/images/'
			cmd = "rm -f %s/%s.qcow " % (folder, name )
			commands.getstatusoutput(cmd)
		self.redirect('/guests/')

'''
	Inserisce la guest in un gruppo
'''
class GuestAddGroup (BaseHandler):
	def get(self):
		pass
	
	def post(self):
		pass

'''
	Elimina la guest dal gruppo
'''
class GuestDelGroup (BaseHandler):
	def get(self):
		pass
	
	def post(self):
		pass

'''
	Imposta la guest come template
'''
class setAsTemplate (BaseHandler):
	def get(self):
		pass
	
	def post(self):
		pass


''' cambia i permessi di un utente'''
class GuestChmodUser (BaseHandler):
	def post(self, guest):
		if self.get_secure_cookie("AuthUsername") == '':
			self.render("NotPermitted.html")
			return
		p= Permission(self.database)
		guest=urllib.unquote(guest)
		if p.verifyUserToGuestPermission(self.get_secure_cookie("AuthUsername"), guest, 3)  == 0:
			self.render("NotPermitted.html")
			return
		act= self.request.arguments['act']
		perm = ['0','0','0','0','0','0','0','0']
		for i in act:
			if i == 'show':
				perm[7]='1'
			if i == 'run':
				perm[6]='1'
			if i == 'delete':
				perm[5]='1'
			if i == 'clone' :
				perm[4]='1'
			if i == 'chmod':
				perm[3]='1'
		perm= int(''.join(perm),2)
		user= self.get_argument('user')
		tmpcursor=self.database.cursor()
		self.cursor.execute("DELETE FROM acl_g2u WHERE guest='%s' AND username='%s'; " % (guest, user))
		if perm > 0:
			tmpcursor.execute("INSERT INTO acl_g2u VALUES ('%s', '%s', %s); " % ( user, guest, str(perm)))
		self.database.commit()
		self.redirect('/guest/%s/' % guest)
