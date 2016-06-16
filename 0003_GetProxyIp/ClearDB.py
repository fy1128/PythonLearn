import MySQLdb


if '__main__' == __name__:
	try:
		dbconnect = MySQLdb.connect(user='baicai', passwd='baicai', db='proxyip')
		dbcursor = dbconnect.cursor()
		dbcursor.execute('delete from LastCaptureTime where Domain="www.xicidaili.com"')
		dbconnect.commit()
		dbcursor.close()
		dbconnect.close()
	except MySQLdb.Error,e:
		print e
	except:
		print 'Unknow error'
