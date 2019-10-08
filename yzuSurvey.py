# -*- coding:utf-8 -*-
#
# 有些元智portal的功能是從舊網頁抓下來的（課表、問卷）這時候要再拿個session去舊網頁抓
# 新版的功能寫在“portalx” 舊的用”portal“
#
# 2017/12/18 更新日誌
#  - 學校新增問卷項目，導致 post 失敗，已改成使用 soup.find_all("input", id="radio") 來製作 payload
# 2018/06/07
#  - 英語授課會有另外的 checkbox
# 2018/12/17
#  - payload btOk 偷換成 btSubmit ：）
# 2019/05/30
#  - payload btOK 又回來了，兩個一起送也會過，就先這樣吧！

import requests
import re
from bs4 import BeautifulSoup


print("######################################")
print("# 元智大學問卷機器人 by 張彥成(Tyze) #")
print("######################################\n")

usrId = raw_input("[*] 請輸入您的學號：")
usrPwd = raw_input("[*] 請輸入您的密碼：")
Header = {
        'Referer': 'https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx',
        'User-Agent': 'Mozilla/5.0 (Yzuuuuuuuuuu) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    	}

s = requests.Session()

print("[*] Started!")

def getNewEnv(bs):
	global _VIEWSTATE
	global _VIEWSTATEGENERATOR
	global _EVENTVALIDATION
	_VIEWSTATE = bs.select('#__VIEWSTATE')[0].get('value')
	_VIEWSTATEGENERATOR = bs.select('#__VIEWSTATEGENERATOR')[0].get('value')
	_EVENTVALIDATION = bs.select('#__EVENTVALIDATION')[0].get('value')

def portalx_login():
	r = s.get("https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx", headers=Header)
	soup = BeautifulSoup(r.text.encode('utf-8'), "lxml")
	getNewEnv(soup)
	loginJSON = {
            '__VIEWSTATE': _VIEWSTATE,
            '__VIEWSTATEGENERATOR': _VIEWSTATE,
            '__EVENTVALIDATION': _EVENTVALIDATION,
            'Txt_UserID': usrId,
            'Txt_Password': usrPwd,
            'ibnSubmit': "登入"
        }

	r = s.post("https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx", data=loginJSON, headers=Header)
	r1 = s.get('https://portalx.yzu.edu.tw/PortalSocialVB/FMain/DefaultPage.aspx?Menu=Default&LogExcute=Y', headers=Header)
	try:
		usrName = str(re.findall('<a[^>]+>([^>]+)<\/a>' ,r1.text.encode('utf-8'))[0]).decode('string_escape')
		print(usrName+' 同學你好！歡迎使用元智課程問卷機器人～')
		logined = True
		pass
	except IndexError:
		print('帳號密碼可能有誤喔～～')
		pass


def portalx_getPayload():
	# set query
	s.get("https://portalx.yzu.edu.tw/PortalSocialVB/FMain/ClickMenuLog.aspx?type=App_&SysCode=A08", headers=Header)
	# 進這個87網站取sessionID 搭配bs4拿值
	r = s.get("https://portalx.yzu.edu.tw/PortalSocialVB/IFrameSub.aspx", headers=Header)
	soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
	payload = {}
	payload["SessionID"] = soup.select('#SessionID')[0].get('value')
	payload["LangVersion"] = soup.select('#LangVersion')[0].get('value')
	payload["Y"] = soup.select('#Y')[0].get('value')
	payload["M"] = soup.select('#M')[0].get('value')
	payload["CosID"] = soup.select('#CosID')[0].get('value')
	payload["CosClass"] = soup.select('#CosClass')[0].get('value')
	payload["UseType"] = soup.select('#UseType')[0].get('value')
	return payload

def portal_getAllSurvey():
	payload = portalx_getPayload()
	loginJSON = {
		"Account":usrId,
		"SessionID":payload["SessionID"],
		"LangVersion":payload["LangVersion"],
		"Y":payload["Y"],
		"M":payload["M"],
		"CosID":payload["CosID"],
		"CosClass":payload["CosClass"],
		"UseType":payload["UseType"]
	}
	s.post("https://portal.yzu.edu.tw/NewSurvey/NewLogin.aspx", data=loginJSON, headers=Header)
	r = s.get("https://portal.yzu.edu.tw/NewSurvey/std/F01_Questionnaire.aspx", headers=Header)
	tmp = re.findall(r"href=\"(.*?)\" target=\"_self\">(.*?)</a>", r.text.encode('utf-8'))
	# 整理問卷
	surveyList = []
	tmp_list = {}
	count = 0
	for item in tmp:
		count = count + 1
		if count == 1:
			tmp_list['url'] = "https://portal.yzu.edu.tw/NewSurvey/std/"+item[0] # url
			tmp_list['classId'] = item[1] # class id
		if count == 3:
			tmp_list['className'] = item[1] # class name
		if count == 4:
			surveyList.append(tmp_list)
			tmp_list = {}
			count = 0
	return surveyList

def printAllSurvey(l):
	for child in l:
		tmp_msg = child['classId'] + " " + child['className'].decode('string_escape')
		print(tmp_msg)

def doSurvey(url, text):
	tmp_r = s.get(url, headers=Header)
	tmp_soup = BeautifulSoup(tmp_r.text.encode('utf-8'), 'lxml')
	getNewEnv(tmp_soup)
	soup = BeautifulSoup(tmp_r.text.encode('utf-8'), 'lxml')
	if len(soup.find(id="2150_1")):
		ta_checked = soup.select('#2150_1')[0].get("checked")
	else:
		ta_checked = None
	payload = {
		"__VIEWSTATE": _VIEWSTATE,
		"__VIEWSTATEGENERATOR":_VIEWSTATEGENERATOR,
		"__EVENTVALIDATION":_EVENTVALIDATION,
		"1473":"上課講解認真、教材豐富。",
		"btSubmit":"完成",
		"btOK":"完成"
	}
	# 2017/12/18 update 學校偷增加幾個新項目需要填寫，寫成這樣好了 (笑)
	items = soup.find_all("input", type="radio")
	for item in items:
		payload[ item.get("name") ] = "1"

	# 2018/06/07 update 英語授課 ($4 是沒進步)
	items = soup.find_all("input", type="checkbox")
	for item in items:
		if item.get("name").count("$4") == 0:
			payload[ item.get("name") ] = "1" 

	if ta_checked != "checked":
		print("此課程可能有助教。")
		payload["2150"] = "1"
		payload["1423"] = "1"
		payload["1424"] = "1"
		payload["1473"] = "老師講課詳細、有很多補充教材、助教認真。"

	if text != "":
		print("自訂文字：" + text)
		payload["1473"] = text
	r = s.post(url, headers=Header, data=payload)
	msg = r.text.encode('utf-8')
	return msg

def doAllSurvey(l):
	for child in l:
		print("[*] 開始填寫問卷 " + child["classId"] + " " + child["className"])
		if doSurvey(child['url'].replace("&amp;", "&"), "").count("問卷填寫完成。") >= 1:
			print("[*] 填寫成功。")
		else:
			print("[*] 填寫失敗。")

portalx_login()

test = portal_getAllSurvey()
print("您未填寫的問卷：")
printAllSurvey(test)
print(' ')
doAllSurvey(test)

print("\n機器人工作完成，如程式有問題請來信至 tyzescgm@gmail.com\n")
raw_input()
