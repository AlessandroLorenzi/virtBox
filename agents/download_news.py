#!/usr/bin/env python
import xml.dom.minidom
import urllib2
import xml.dom
import datetime

'''
CONFIGURAZIONE
'''
num_news = 5
link = "http://news.google.it/news?hl=it&q=virtualizzazione&um=1&ie=UTF-8&output=rss"
file_path= "/home/virtmaster/virtBox/static/news.html"
row= "<li class='news%s'><a href='%s'>%s</a></li>"
'''
FINE CONFIGURAZIONE
'''

rss= urllib2.urlopen(link)
file= rss.read()
dom1 = xml.dom.minidom.parseString(file)
file = open(file_path, 'w')

now = datetime.datetime.now()
date= now.strftime("%Y-%m-%d %H:%M")

file.write("<html><head/><body><!-- Generated %s--><ul id='news_list'>" % date)


for item in dom1.getElementsByTagName("item"):
	title =item.getElementsByTagName("title").item(0)
	title = title.toxml()[7:-8]
	
	link =item.getElementsByTagName("link").item(0)
	link = link.toxml()[6:-7]
	try:
		file.write(row% ( str(num_news % 2),link,title.encode("utf-8") ) )
		num_news -= 1
		if num_news <= 0:
			break
	except UnicodeDecodeError:
		print("Error")
		
	
file.write("</ul><img src='http://www.gstatic.com/news/img/logo/it_it/news.gif' style= 'width: 100px; '  /></body></html>")
file.close()
