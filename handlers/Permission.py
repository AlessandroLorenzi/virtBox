class Permission ():
	global dbconn
	def __init__(self, dbconn):
		self.dbconn = dbconn
		
	def verifyUserToGuestPermission(self, username, guest, permission) :
		cursor = self.dbconn.cursor()
		cursor.execute("SELECT acl_g2u.permissions AS perm FROM acl_g2u WHERE guest = '%s' AND username = '%s'" % (guest, username ) )
		self.dbconn.commit()
		perm = 0
		for perm_row in cursor:
			''' <madness > '''
			permbyte = '{0:08b}'.format(perm_row[0]) 
			''' </madness> '''
			perm += int(permbyte[permission])
		if perm > 0:
			perm = 1
		return perm


	def verifyUserPermission (self):
		cursor = self.dbconn.cursor()
		cursor.execute("SELECT acl_u.perm AS perm FROM acl_u2g WHERE guest = '%s' AND user = %s" % (guest,str(username) ) )

		self.dbconn.commit()
		perm = 0
		for perm_row in cursor:
			perm += int(str(bin(perm_row[0])[2:])[campo])
		if perm > 0:
			perm = 1
		return perm
	
	def verifyGuestPermession (self):
		cursor = self.dbconn.cursor()
		cursor.execute("SELECT acl_g.perm AS perm FROM acl_u2g WHERE guest = '%s' AND user = %s" % (guest,str(username) ) )

		self.dbconn.commit()
		perm = 0
		for perm_row in cursor:
			perm += int(str(bin(perm_row[0])[2:])[campo])
		if perm > 0:
			perm = 1
		return perm

