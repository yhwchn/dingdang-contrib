# -*- coding: utf-8 
#author: chenzhuo
#date:08/01 2017
#Raspberry Pi or other platform can connect to the mqtt client,publisher and subscriber can access to bidirectional communication by switching their identities.
#Example:you can get temperature of the enviroment collected by Arduino using Raspberry Pi when Raspberry Pi and Arduino communicate with each other.
#The actions' file must be /home/pi/action.txt

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["BUGUANG","JIAOSHUI"]
SLUG = "mqttPub"

def handle(text,mic,profile,wxbot=None):
	logger = logging.getLogger(__name__)

	#get config
	if ( SLUG not in profile ) or ( not profile[SLUG].has_key('host') ) or ( not profile[SLUG].has_key('port') ) or ( not profile[SLUG].has_key('topic_p') ) or ( not profile[SLUG].has_key('topic_s') ):
		mic.say("主人，配置有误")
		return

	host = profile[SLUG]['host']
	port = profile[SLUG]['port']
	topic_s = profile[SLUG]['topic_s']
	topic_p = profile[SLUG]['topic_p']
	text = text.split("，")[0]   #百度语音识别返回的数据中有个中文，

	try:
		mic.say("已经接收到指令")
		mqtt_contro(host,port,topic_s,topic_p,text,mic)
	except Exception, e:
		logger.error(e)
		mic.say("抱歉出了问题")
		return

def isValid(text):
	f = open("/home/pi/action.txt")
	lines = f.readlines()
	words = []
	for line in lines:
		words.append(line.split()[0])
	#words = [u"补光",u"浇水",u"土壤湿度",u"环境温度",u"环境湿度",u"光强",u"光照强度"] #this should be a words file
	return any(word in text for word in words)

class mqtt_contro(object):

	def __init__(self,host,port,topic_s,topic_p,message,mic):
		self._logger = logging.getLogger(__name__)
		self.host = host
		self.port = port
		self.topic_s = topic_s
		self.topic_p = topic_p
		self.message = message
		self.mic = mic
		self.mqttc = mqtt.Client()
		self.mqttc.on_message = self.on_message
		self.mqttc.on_connect = self.on_connect
		#mqttc.on_publish = on_publish
		#mqttc.on_subscribe = on_subscribe
		#mqttc.on_log = on_log
		if self.host and self.topic_p:
			publish.single(self.topic_p, self.message, hostname=self.host)
		if self.port and self.topic_s and self.host:
			self.mqttc.connect(self.host, self.port, 60)
			self.mqttc.subscribe(topic_s, 0)
			self.mqttc.loop_forever()

	def on_connect(self,mqttc, obj, flags, rc):
		if rc == 0:
			pass
		else:
			print("error connect")

	def on_message(self,mqttc, obj, msg):
    	#print(str(msg.payload))
		if msg.payload:
			self.mqttc.disconnect()
			self.mic.say( str(msg.payload) )

	def on_publish(self,mqttc, obj, mid):
		print("mid: " + str(mid))

	def on_subscribe(self,mqttc, obj, mid, granted_qos):
		print("Subscribed: " + str(mid) + " " + str(granted_qos))

	def on_log(self,mqttc, obj, level, string):
		print(string)