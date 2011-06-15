#!/usr/bin/env python
import libvirt
import xml.dom 
from xml.dom import minidom
import os, sys
import commands

conn = libvirt.open('qemu:///system')

for id in conn.listDomainsID():

	dom = conn.lookupByID(id)
	#print dom.XMLDesc(0)
	print "Dom %s  State %s" % ( dom.name(), dom.info()[0] )

	print dom.virDomainGetJobInfo()
	
