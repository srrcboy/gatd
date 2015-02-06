
"""
This module takes in a stream and stores that stream in a capped collection.
"""

import pika
import pymongo

import gatdBlock
import gatdConfig
import gatdLog

l = gatdLog.getLogger('streamer')

mdb = None

def connect_mongodb ():
	# get a mongo connection
	mc = pymongo.MongoClient(host=gatdConfig.mongo.HOST,
	                         port=gatdConfig.mongo.PORT)
	mdb = mc['gatdv6']
	mdb.authenticate(gatdConfig.blocks.MDB_USERNAME,
	                 gatdConfig.blocks.MDB_PASSWORD)

	return mdb


def save (args, channel, method, prop, body):
	global mdb

	try:
		# No magic here, just try to insert the record into the capped collection
		mdb[str(args.uuid)].insert(body)

		channel.basic_ack(delivery_tag=method.delivery_tag)

	except pymongo.errors.AutoReconnect as e:
		l.exception('Going to try to reconnect to mongodb.')

	except pymongo.errors.ConnectionFailure as e:
		l.exception('Lost connection to mongodb.')
		mdb = connect_mongodb()

	except:
		l.exception('Other exception in streamer')


def init (args):
	global mdb
	mdb = connect_mongodb()

	try:
		# Make sure that the capped collection exists
		mdb.create_collection(name=str(args.uuid),
		                      capped=True,
		                      size=1073741824) # 1.0 GB in bytes
	except pymongo.errors.CollectionInvalid:
		# Already exists
		pass


# Start the connection to rabbitmq

description = 'Streaming'
settings = []
parameters = [('socketio_url', str), ('websocket_url', str)]

gatdBlock.start_block(l, description, settings, parameters, save, init=init)