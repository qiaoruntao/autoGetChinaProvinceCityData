# -*- coding: utf-8 -*-  
import urllib2
import urllib
import bs4
import re
import uniout
from pprint import pprint
import json


def getPageUrl():
	#return "http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201504/t20150415_712722.html"
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : user_agent }
	values = {'name':'Michael Foord',
	          'location':'Northampton',
	          'language':'Python' }
	pageUrl="http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/";
	data = urllib.urlencode(values)
	req = urllib2.Request(pageUrl, data, headers)
	response = urllib2.urlopen(req)
	soup = bs4.BeautifulSoup(response.read(), "html.parser")
	#pprint(soup.get_text()), text=re.compile(u"最新县及县以上行政区划代码")
	targetUl=soup.find_all(class_='center_list_contlist')
	#print targetUl
	aArray=targetUl[0].find_all('a')
	#print aArray
	resultUrl=pageUrl+aArray[0].get('href')[2:]
	return resultUrl
	#return [a.attrs.get('href') for a in soup.select('div.video-summary-data a[href^=/video]')]
	#return
def getRawData(pageUrl):
	response = urllib2.urlopen(pageUrl)
	soup = bs4.BeautifulSoup(response.read(), "html.parser")
	pairedData=soup.find_all('p', class_='MsoNormal')
	rawData=[]
	pattern = re.compile(r'([\d]+)[\s]+([\S]+)')
	for pair in pairedData:
		rawText=pair.text
		rawText=rawText.replace(u'\u3000', u'')
		rawText=rawText.replace(u'\u00A0', u'')
		match = pattern.match(rawText)
		if match==0:
			print "error: cannot recognize data="+rawText
			continue
		print "0="+match.group(1)+",1="+match.group(2)
		rawData.append([match.group(1), match.group(2)])
	return rawData
def formatData(rawData):
	provinceData=[]
	citiesData={}
	townsData={}
	provincePattern = re.compile(r'([\d]{2})0000')
	cityPattern = re.compile(r'([\d]{4})00')
	currentProvince=""
	currentCity=""
	isTownToCity=0
	tempCitiesArray=[]
	tempTownsArray=[]
	for pairRawData in rawData:
		provinceMatch=provincePattern.match(pairRawData[0])
		if provinceMatch:
			#处理省一级单位
			print "find province, first two code="+provinceMatch.group(1)
			isTownToCity=0#更换省一级单位, 重新检查是否为直辖市等情况
			if tempCitiesArray:
				#数组不为空, 推入之前的城市数据
				print "push cities, province=",
				pprint(currentProvince),
				print ", array=",
				pprint(tempCitiesArray)
				citiesData[currentProvince]=tempCitiesArray
				tempCitiesArray=[]
			#推入这个省级单位数据
			provinceData.append(pairRawData[1])
			currentProvince=pairRawData[1]
			continue
		cityMatch=cityPattern.match(pairRawData[0])
		if cityMatch:
			if pairRawData[1]!=u"市辖区" and pairRawData[1]!=u"县" and pairRawData[1]!=u"自治区直辖县级行政区划" and pairRawData[1]!=u"省直辖县级行政区划":
				#处理市一级单位
				print "find city, first four code="+cityMatch.group(1)+",name="+pairRawData[1]
				if tempTownsArray:
					#之前有县级数据
					townsData[currentCity]=tempTownsArray
					tempTownsArray=[]
				#推入该城市的数据
				tempCitiesArray.append(pairRawData[1])
				currentCity=pairRawData[1]
			else:
				#是直辖市等情况, 将县一级单位提升为市一级
				print "province "+currentProvince+" is zhixiashi"
				isTownToCity=1
			continue
		#此时剩下的只有县级单位了
		if isTownToCity:
			#县级单位转市级单位
			print "find town to city case, name="+pairRawData[1]
			tempCitiesArray.append(pairRawData[1])
			currentCity=pairRawData[1]
			continue
		elif pairRawData[1]!=u"市辖区":
			#其他县级单位
			tempTownsArray.append(pairRawData[1])
	print "provinceData="
	pprint(provinceData)
	print "citiesData="
	pprint(citiesData)
	# print "townsData="
	# pprint(townsData)
	coutAsJs(provinceData, citiesData, townsData)
def coutAsJs(provinceData, citiesData, townsData):
	resultStr="var provinces=["
	for province in provinceData:
		resultStr+="'"+province+"',"
	resultStr+="];\n"
	resultStr+="var citiesV={};\n"
	for provinceName, cityArray in citiesData.items():
		resultStr+="citiesV['"+provinceName+"']=["
		for cityName in cityArray:
			resultStr+="'"+cityName+"',"
		resultStr+='];\n'
	pprint(resultStr)
formatData(getRawData(getPageUrl()))
#print getPageUrl()