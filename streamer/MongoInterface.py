import os
import pymongo
import sys
import time

sys.path.append(os.path.abspath('../config'))
import gatdConfig

class MongoInterface:

	def __init__(self):
		# Connect to the mongo database
		try:
			self.mongo_conn = pymongo.MongoClient(host=gatdConfig.mongo.HOST,
			                                      port=gatdConfig.mongo.PORT)
			self.mongo_db = self.mongo_conn[gatdConfig.mongo.DATABASE]
			if gatdConfig.mongo.USERNAME:
				self.mongo_db.authenticate(gatdConfig.mongo.USERNAME,
				                           gatdConfig.mongo.USERNAME)
			self.stop = False

		except pymongo.errors.ConnectionFailure:
			print "Could not connect. Check the host and port."
			sys.exit(1)

	def get (self, query):

		# Trial period:
		# Let's just use this capped collection for everything cause why not
		# try.
		# time is the milliseconds in the past from now to start getting
		# data from.
		now = int(round(time.time() * 1000))
		if 'time' in query:
			start = now - query['time']
		else:
			start = now
		query['time'] = {'$gt': start}

		# We are only streaming out of the tailable capped collection
		# Make sure we only get packets from now onward
	#	now = int(round(time.time() * 1000))
	#	query['time'] = {'$gt': now}

		cursor = self.mongo_db[gatdConfig.mongo.COL_FORMATTED_CAPPED].find(query,
			tailable=True,
			await_data=True)
		while cursor.alive and not self.stop:
			try:
				n = cursor.next()
				n['_id'] = str(n['_id'])
				yield n
			except StopIteration:
				pass


	def __del__ (self):
		self.mongo_conn.close()