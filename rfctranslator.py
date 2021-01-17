#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import http.client
import hashlib
import json
import urllib
import random
import time
import shutil
import os
import sys

def downloadHtmlPage(url,tmpf = ''):
	i = url.rfind('/')
	fileName = url[i+1:]
	if tmpf :
		fileName = tmpf
	print (url + "->" + fileName)
	urllib.request.urlretrieve(url,fileName)
	print ('Downloaded ' + fileName	)
	time.sleep(0.2)
	return fileName


def baidu_translate(content):
	appid = '20200614000494887'  # 填写你的appid
	secretKey = 'Xng8ScG54GURtCkkRIhI'  # 填写你的密钥
	httpClient = None
	myurl = '/api/trans/vip/translate'
	fromLang = 'en'   #原文语种
	toLang = 'zh'   #译文语种
	salt = random.randint(32768, 65536)
	q = content
	sign = appid + q + str(salt) + secretKey
	sign = hashlib.md5(sign.encode()).hexdigest()
	myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
	salt) + '&sign=' + sign
	try:
		httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
		httpClient.request('GET', myurl)
		# response是HTTPResponse对象
		response = httpClient.getresponse()
		result_all = response.read().decode("utf-8")
		js = json.loads(result_all)
		print (js)
		dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
		return dst
				
	except Exception as e:
		print (e)
	finally:
		if httpClient:
			httpClient.close()
			

def translateRFCs(srcfile, dstfile):
	rfcfile_en = open(srcfile)
	rfcfile_cn = open(dstfile, "w+", encoding='utf-8')

	#实例化
	#Contents或Table of Contents
	#translator = Translator(service_urls=['translate.google.cn'])
	str_cn = ''
	tmp = ''
	rn_flag = 0
	rstr = rfcfile_en.readline()
	rstr.lstrip()
	while (rstr != ''):
		r1 = re.match('^\d.', rstr)
		r2 = re.match('^\w\)', rstr)
		r3 = rstr.find('• ')
		r4 = rstr.find('- ')
		r5 = rstr.find('. ')
		r6 = re.match('^\d-', rstr)
		r7 = re.match('.\n$', rstr)
        
		#l1 = len(rstr)
		if ((rstr.count('_') > 5) or (rstr.count('-') > 5) or (rstr.count('+') > 5) or (rstr.count('.') > 5)) :
			if (tmp != '') :
				str_cn = baidu_translate(tmp)
				time.sleep(1)
				if str_cn != None :
					str_cn = str_cn + '\r\n'
					rfcfile_cn.write(str_cn)
				else :
					rfcfile_cn.write(tmp)
					rn_flag = 0
				tmp = ''
			rfcfile_cn.write(rstr)
			print ("rstr: " + rstr)
			print ("tmp: " + tmp)
			rstr = rfcfile_en.readline()
			rstr.lstrip()
			continue
		if ((r1 != None) or (r2 != None) or (r3 == 0) or (r4 == 0) or (r5 == 0) or (r6 != None)) :
			if (tmp != '') :
				str_cn = baidu_translate(tmp)
				time.sleep(1)
				if str_cn != None :
					str_cn = str_cn + '\r\n'
					rfcfile_cn.write(str_cn)
				else :
					rfcfile_cn.write(tmp)
					rn_flag = 0
				tmp = ''
			tmp = tmp + rstr[:-1] + ' '
			rn_flag = 0
		elif ((rstr != '\n') and (r7 == None)) :
			tmp = tmp + rstr[:-1] + ' '
			rn_flag = 0
		elif ((rstr == '\n' and tmp != '') or (r7 != None)) :
			#str_cn = translator.translate(tmp, dest='zh-CN').text
			str_cn = baidu_translate(tmp)
			time.sleep(1)
			if str_cn != None :
				str_cn = str_cn + '\r\n'
				rfcfile_cn.write(str_cn)
				str_cn = str_cn + '\r\n'
			else :
				rfcfile_cn.write(tmp)
			rn_flag = 0
			tmp = ''
		elif (rstr == '\n' and tmp == '' and rn_flag == 0) :
			rfcfile_cn.write("\r\n")
			rn_flag = 1
			
		print ("rstr: " + rstr)
		print ("tmp: " + tmp)
		rstr = rfcfile_en.readline()
		rstr.lstrip()

	rfcfile_en.close()
	rfcfile_cn.close()

# http://www.networksorcery.com/enp/rfc/rfc1000.txt
# http://www.networksorcery.com/enp/rfc/rfc6409.txt
if __name__ == '__main__':
	dirPath = "RFC"
	addr = 'http://www.ietf.org/rfc'
	if len(sys.argv) < 2 :
		#addr = 'http://www.networksorcery.com/enp/rfc'
		startIndex = 4
		#startIndex = int(raw_input('start : '))
		endIndex = 8640
		#endIndex = int(raw_input('end : '))
		if startIndex > endIndex :
			print ('Input error!'		)
		if False == os.path.exists(dirPath):
			os.makedirs(dirPath)
		fileDownloadList = []
		logFile = open("log.txt","w")
		for i in range(startIndex,endIndex+1):
			try:
				t_url = '%s/rfc%s.txt' % (addr, '{:0>4d}'.format(i))
				print (t_url)
				fileName = downloadHtmlPage(t_url)
				oldName = './'+fileName
				newName = './'+dirPath+'/'+fileName
				if True == os.path.exists(oldName):
					shutil.move(oldName,newName)
					print ('Moved ' + oldName + ' to ',newName)
					translateRFCs(newName, newName[:-4]+'_cn.txt')
			except:
				msgLog = 'get %s failed!' % (i)
				print (msgLog)
				logFile.write(msgLog+'\n')
				continue
		logFile.close()
	else :
		try:
			fileNames = sys.argv[1:]
			for fileName in fileNames :
				oldName = './' + fileName
				newName = './' + dirPath + '/' + fileName
				if True == os.path.exists(oldName):
					shutil.move(oldName, newName)
					print ('Moved ' + oldName + ' to ', newName)
					translateRFCs(newName, newName[:-4] + '_cn.txt')
		except Exception as e:
			msgLog = 'get file failed!'
			print (msgLog)
			print (e)
		#	logFile.write(msgLog + '\n')


