#! python3
# -*- coding: utf-8 -*-
#辉光字幕组NixieSubs
#Voicebase API: davidzz
#匹配算法: davidzz不愿透露姓名的朋友
#整合，中英合并，格式化: Kilo19 (Kilo_One_Nine)
'''
需要安装python 3，注意安装时勾选"add Python to PATH"
txt：要打轴的原文
json: Voicebase API识别结果，注意认准[NCE开头或_trans结尾，不要与其他JSON混淆
'''
# 未来想把diff功能做进去
import difflib
import codecs
import json
import sys
import re
import os

subType = {
	'LTT intro': 0, 'Annotation': 1,
	'Chi': 2, 'Eng': 3, 'Note': 4
}

rawTags = ['LTT intro', '辉注', '辉中', '辉英', '辉注']

def show_exception_and_exit(exc_type, exc_value, tb):
	import traceback
	traceback.print_exception(exc_type, exc_value, tb)
	input('''脚本遇到错误，请截图此画面发送给Kilo19。按回车键退出
	Error encountered, please send a screenshot of this error to Kilo19
	Press Enter to Exit
	''')
	sys.exit(-1)

sys.excepthook = show_exception_and_exit

tl = [('\u2013', '\u002D')]
def ReplaceNaughtyCharacters(source, troubleList):
	dirName, baseName = os.path.split(source)
	for troubleMaker in troubleList:
		if troubleMaker[0] in baseName:
			baseName = baseName.replace(
				troubleMaker[0], troubleMaker[1]
			)
	newSource = os.path.join(dirName, baseName)
	print(newSource)
	os.rename(source, newSource)
	return newSource

def format_text(text):
	text = text.replace('-', ' ')
	return re.sub(r"[^a-z0-9 ]+", "", text.lower())

def filter_json(words):
	new_words = [word for word in words if word['w'] != '.']
	return new_words

def convert_time(ms):
	# WARNING: please correct this if it failed to work
	return "%d:%02d:%05.2f" % (
				ms // 3600000,
				(ms % 3600000) // 60000,
				(ms % 60000) / 1000
			)

def get_lcs(S, T):
	n = len(S)
	m = len(T)
	dp = [[0 for j in range(m + 1)] for i in range(n + 1)]
	s = [(0, -1)] * n
	for i in range(n):
		for j in range(m):
			if S[i] == T[j]:
				dp[i + 1][j + 1] = dp[i][j] + 1
				if dp[i][j] + 1 > s[i][0]:
					s[i] = (dp[i][j] + 1, j)
			else:
				dp[i + 1][j + 1] = max(
					dp[i + 1][j], dp[i][j + 1]
				)
	return [a[1] for a in s]

def get_lis(s):
	#有数字括号在s中位置代表欲匹配文章哪个点与机扒匹配
	#括号中数字代表与机扒列表中哪个词匹配
	n = len(s)
	dp = [1] * n
	ls = [-1] * n
	ret = [()] * n
	for i in range(1, n):
		mxv = 0
		ptr = -1
		for j in range(i):
			if s[j] < s[i] and dp[j] > mxv:
				mxv = dp[j]
				ptr = j
		dp[i] = mxv + 1
		ls[i] = ptr
	last = dp.index(max(dp))
	ret[last] = (s[last],)
	#backtracking
	while ls[last] != -1:
		last = ls[last]
		ret[last] = (s[last],)
	return ret

def regularize(lis, tot):
	n = len(lis)
	mismatched = []
	i = 0
	while i < n:
		if lis[i] != ():
			i += 1
		else:
			j = i
			while j < n and lis[j] == ():
				j += 1
			#lis中，哪对括号开始连续空(i)，空到哪里结束(j)
			#i是空的开始，j是非空的开始
			mismatched.append((i, j))
			i = j
	for l, r in mismatched:
		if l > 0:
			#机扒第几个单词开始连续不匹配
			#h是不匹配的开始
			h = lis[l - 1][0] + 1
		else:
			h = 0
		if r < n:
			#机扒第几个单词开始重新匹配
			#m是匹配的开始
			m = lis[r][0]
		else:
			#匹配到机扒识别结尾(也越界)
			m = tot
		#m-h <= 1，说明不匹配和匹配距离足够近
		#同时机扒不匹配长度可能远远小于待匹配中的不匹配长度
		if h + 1 >= m:
			for i in range(l, r):
				#lis中间的空隙都填上不匹配的开始
				lis[i] = (h,)
		else:
			#机扒中不匹配长度除以待匹配中的不匹配长度
			avg = (m - h) / (r - l)
			for i in range(l, r - 1):
				#按长度均匀填上可能匹配的词
				#此时一个tuple代表待匹配原文这个词
				#(应该对应机扒词的开始,应对应机扒词的结束)
				lis[i] = tuple(range(round(h), round(h + avg)))
				h += avg
			lis[r - 1] = tuple(range(round(h), m))
	return lis

lineProperties = [
	'Format', 'Layer',
	'Start', 'End',
	'Style', 'Name',
	'MarginL', 'MarginR', 'MarginV',
	'Effect',
	'Text'
]

toNumber = [
	'Layer',
	'MarginL', 'MarginR', 'MarginV',
]

toTimestamp = [
	'Start', 'End',
]

class AegiLine:
	lineDict = None
	def __init__(self, line, lineType):
		self.lineDict = dict((k, '') for k in lineProperties)
		self.lineDict['Style'] = rawTags[lineType]

		if lineType == subType['Note']:
			self.lineDict['Format'] = "Comment"
		else:
			self.lineDict['Format'] = "Dialogue"

		if lineType == subType['LTT intro']:
			self.lineDict['Text'] = r'{\pos(640,630)\fad(400,0)}' + line
		else:
			self.lineDict['Text'] = line

		for k in toNumber + toTimestamp:
			self.lineDict[k] = 0

	@classmethod
	def fromDict(cls, initDict):
		aLine = cls('', subType['Chi'])
		for k in lineProperties:
			aLine.lineDict[k] = initDict[k]

	def setTime(self, start, end):
		self.lineDict['Start'] = start
		self.lineDict['End'] = end

	def dumps(self):
		serializedList = []
		for k in lineProperties:
			serializedList.append(self.lineDict[k])
		for k in toTimestamp:
			serializedList[
				lineProperties.index(k)
			] = convert_time(self.lineDict[k])
		for k in toNumber:
			serializedList[
				lineProperties.index(k)
			] = str(self.lineDict[k])
		outString = serializedList[0] + ': ' + \
					','.join(serializedList[1:])
		return outString

def indexOfAllOccurences(searchFrom, searchFor):
	index = 0
	results = []
	while index < len(searchFrom):
		index = searchFrom.find(searchFor, index)
		if index == -1:
			break
		else:
			results.append(index)
		index += len(searchFor)
	return results

def timestamp2ms(ts):
	tsPair = ts.split(',')
	base = [3600E3, 60E3, 1E3]
	totalTime_ms = sum(
		[
			a*b for a,b in zip(
				base, map(
					float, tsPair[0].split(':')
				)
			)
		]
	)
	return int(totalTime_ms)

def parseLineFromASS(line):
	lineDict = {}
	splits = line.split(':', 1)
	splits = [splits[0]] + splits[1].split(',', 9)
	for index, key in enumerate(lineProperties):
		lineDict[key] = splits[index]
	for k in toNumber:
		lineDict[k] = int(lineDict[k])
	for k in toTimestamp:
		lineDict[k] = timestamp2ms(lineDict[k])
	return AegiLine.fromDict(line)

def isVoidLine(line):
	return len(line) == 0

def isChiChar(zi):
	return 0x4E00 <= ord(zi) <= 0x9FFF

def isChinese(line):
	hasNoEngChar = True
	for c in line:
		if isChiChar(c):
			return True
		else:
			hasNoEngChar = hasNoEngChar and not(c.isalpha())

	return False or hasNoEngChar

def judgeType(line):
	if line[0:9].lower() == 'ltt intro':
		return subType['LTT intro']
	if line.find('※') != -1:
		return subType['Annotation']
	if re.match(r'[（\(]*轴[：:\uff1a] *', line) or line[:2] == '//':
		return subType['Note']
	if isChinese(line):
		return subType['Chi']
	return subType['Eng']

def deBracket(line):
	if line[0] == '(' and line[1] == ')':
		return line[1:-1]
	else:
		return line

def PreFormatLine(line):
	if len(line) == 0:
		return line
	line = line.replace('', '')
	line = line.replace('', '')
	line = line.replace('“', '\"')
	line = line.replace('”', '\"')
	line = line.replace('：', ': ')
	line = line.replace('’', '\'')
	line = line.replace('‘', '\'')
	line = line.replace('♂', '')
	line = line.replace('？', '? ')
	line = line.replace('（', ' (')
	line = line.replace('）', ') ')
	line = line.replace('﻿', '')
	line = re.sub(r'^[（\\(]*注[：:\uff1a] *', '※', line)
	if line.find('[') != -1:
		line = re.sub(r'\[([^]]*)\]\(http[^]]*\)', r'\1', line)
	return line.strip()

def engFormat(line):
	line = re.sub('[，。、,]', ', ', line)
	line = re.sub(' {2,}', ' ', line)
	return line

def FormatChiSpace(line):
	start = 1
	while True:
		start = line.find(' ', start)
		if start < 0 or start >= len(line) - 1:
			return line
		if isChiChar(line[start - 1]) and isChiChar(line[start + 1]):
			line = line[:start] + ' ' + line[start:]
		start += 2 # use start += 1 to find overlapping matches
	return line

def FormatQuoteSpace(line):
	start = 0
	oddQuote = True
	while True:
		start = line.find('"', start)
		if start == 0:
			oddQuote = not oddQuote
			start += 1
			continue

		if start == -1 or start == len(line) - 1:
			return line

		if oddQuote:
			if isChiChar(line[start - 1]):
				line = line[:start] + ' ' + line[start:]
				start += 1
			if line[start + 1] == ' ' and line[start + 2] != ' ':
				line = line[:start + 1] + line[start + 2:]
		else:
			if line[start - 1] == ' ' and line[start - 2] != ' ':
				line = line[:start - 1] + line[start:]
				start -= 1
			if isChiChar(line[start + 1]):
				line = line[:start + 1] + ' ' + line[start + 1:]

		start += 1
		oddQuote = not oddQuote
	return line

def chiFormat(line):
	line = re.sub('[，。、]', '  ', line)
	line = re.sub(' {3,}', '  ', line)
	line = FormatChiSpace(line)
	line = FormatQuoteSpace(line)
	return line

def annotationFormat(line):
	line = deBracket(line)
	return line

def introFormat(line):
	line = re.sub('^ *\(', '', line)
	line = re.sub('\) *$', '', line)
	line = re.sub(
				'^LTT intro *[:：\uff1a] *', '',
				line, flags = re.IGNORECASE
			)
	return line

def Format(line, lineType):
	if lineType == subType['Eng']:
		line = engFormat(line)
	else:
		line = chiFormat(line)
	if lineType == subType['Annotation']:
		line = annotationFormat(line)
	if lineType == subType['LTT intro']:
		line = introFormat(line)
	return line.strip()

if __name__ == '__main__':
	#Your style will bring the new smile - Zytokine GOLD
	aegiHead = '''[Script Info]
; Script generated by Full-auto_M134_public
; http://www.nixiesubs.com/
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1280
PlayResY: 720

[Aegisub Project Garbage]
Last Style Storage: Default

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,35,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,8,1
Style: 半透背景,Microsoft YaHei,40,&H00FFFFFF,&H000000FF,&H85000000,&H6F000000,0,0,0,0,100,100,0,0,3,0,1.5,2,0,0,8,1
Style: Logo,Microsoft YaHei,35,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,8,1
Style: 辉中,文泉驿微米黑,45,&H00FFFFFF,&H000000FF,&H006E4216,&H00000000,-1,0,0,0,100,100,0.5,0,1,2.8,0.2,2,0,0,10,1
Style: 辉英,Tahoma,35,&H00FFFFFF,&H000000FF,&H003B3C3D,&H00000000,0,0,0,0,100,100,1,0,1,2.8,0.2,2,0,0,10,1
Style: 辉注,文泉驿微米黑,36,&H00000000,&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,3,0.7,9,10,10,10,1
Style: LTT intro,Noto Sans CJK SC Medium,60,&H00494949,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Comment: 0,0:00:00.00,0:00:00.01,Default,,0,0,0,,选中此行以检查漏掉的行
'''.replace('\n', '\r\n')

	nixieLogo_LTT_intro = '''Dialogue: 0,0:00:00.00,0:00:00.00,Logo,,0,0,0,,If you use "LTT intro:" to start a line, this logo will appear alongside it
'''.replace('\n', '\r\n')

	nixieLogo_LMG_no_intro = '''Dialogue: 0,0:00:00.00,0:00:08.00,Logo,,0,0,0,,If none of your lines starts with "LTT intro:" then this will appear at the beginning of your video
'''.replace('\n', '\r\n')

	recogPath = None
	if len(sys.argv) == 2:
		sourcetext = sys.argv[1].replace('\"', '').strip()
	elif len(sys.argv) == 3:
		sourcetext = sys.argv[1].replace('\"', '').strip()
		recogPath = sys.argv[2].replace('\"', '').strip()
	else:
		print('Drag Text File Here. Unicode Only!')
		sourcetext = input().replace('\"', '').strip()
		print('Drag Voicebase Json Here. Unicode Only! Just hit enter if none')
		recogPath = input().replace('\"', '').strip()

	processed = os.path.splitext(sourcetext)[0] + '.ass'

	recogJson = None
	recogWordsWithTime = []
	recogWords = []
	if os.path.isfile(recogPath):
		recogFile = codecs.open(recogPath, 'r', 'utf-8')
		recogJson = json.load(recogFile)
		recogFile.close()
		# Voicebase v3
		if "transcript" in recogJson.keys():
			recogWordsWithTime = recogJson["transcript"]["words"]
		# Voicebase v2
		else:
			recogWordsWithTime = recogJson["media"]["transcripts"]["latest"]["words"]
		recogWordsWithTime = filter_json(recogWordsWithTime)
		recogWords = [
			format_text(recogWordWithTime["w"])
				for recogWordWithTime in recogWordsWithTime
		]
	x = 0

	while os.path.isfile(processed):
		processed = ''.join(
			[os.path.splitext(sourcetext)[0], '_', str(x), '.ass']
		)
		x += 1

	mainLines = []
	extraLines = {}
	buf = []
	introExist = False
	numTotalLine = 0
	targetWords = []
	lenEngLines = []
	subfile = codecs.open(sourcetext, 'r', 'utf-8')
	for line in subfile:
		line = PreFormatLine(line)
		if isVoidLine(line):
			continue
		lineType = judgeType(line)
		if lineType == subType['LTT intro']:
			introExist = True
		line = Format(line, lineType)

		buf.append((line, lineType))
		if buf[0][1] == subType['Eng']:
			if len(buf) == 2:
				if buf[1][1] == subType['Chi']:
					mainLines.append(
						AegiLine(
							buf[1][0] + '\\N{\\r辉英}' +
							buf[0][0], subType['Chi']
						)
					)
					if recogWordsWithTime:
						targetWordsInsert = format_text(buf[0][0]).split()
						targetWords.extend(targetWordsInsert)
						lenEngLines.append(
							len(targetWordsInsert)
						)
					buf.clear()
					numTotalLine += 1
				elif buf[1][1] == subType['Eng']:
					extraLines[numTotalLine] = AegiLine(buf[0][0], buf[0][1])
					buf.pop(0)
					numTotalLine += 1
				elif buf[1][1] == subType['Note']:
					numTotalLine += 1
					extraLines[numTotalLine] = AegiLine(buf[1][0], buf[1][1])
					buf.pop(1)
				else:
					extraLines[numTotalLine] = AegiLine(buf[0][0], buf[0][1])
					numTotalLine += 1
					extraLines[numTotalLine] = AegiLine(buf[1][0], buf[1][1])
					numTotalLine += 1
					buf.clear()
		else:
			extraLines[numTotalLine] = AegiLine(buf[0][0], buf[0][1])
			buf.pop(0)
			numTotalLine += 1
	subfile.close()

	if buf:
		extraLines[numTotalLine] = AegiLine(buf[0][0], buf[0][1])
		buf.pop(0)
		numTotalLine += 1

	engLinePos = []
	if recogWords:
		lcs = get_lcs(targetWords, recogWords)
		lis = get_lis(lcs)
		lis = regularize(lis, len(recogWords))
		lineHeadPos = 0
		lineTailPos = 0
		lenRecogWords = len(recogWordsWithTime)

		for i in range(len(lenEngLines)):
			lineTailPos += lenEngLines[i]
			if len(lis[lineHeadPos]) == 0 or len(lis[lineTailPos - 1]) == 0:
				mainLines[i].setTime(0, 0)
			else:
				lisLineHead = lis[lineHeadPos][0]
				lisLineTail = lis[lineTailPos - 1][-1]
				if lisLineHead >= lenRecogWords or lisLineTail >= lenRecogWords:
					mainLines[i].setTime(0, 0)
				else:
					mainLines[i].setTime(
						recogWordsWithTime[lisLineHead]['s'],
						recogWordsWithTime[lisLineTail]['e']
					)
			lineHeadPos = lineTailPos

	destination = codecs.open(processed, 'w', 'utf-8')
	destination.write('\ufeff')
	destination.write(aegiHead)
	if not introExist:
		destination.write(nixieLogo_LMG_no_intro)

	mainIter = iter(mainLines)
	for i in range(numTotalLine):
		if not i in extraLines.keys():
			try:
				destination.write(
					next(mainIter).dumps() + '\r\n'
				)
			except:
				pass
		else:
			if extraLines[i].lineDict['Style'] == 'LTT intro':
				destination.write(nixieLogo_LTT_intro)
			destination.write(extraLines[i].dumps() + '\r\n')
	destination.close()
	print('Done! Path:')
	print(processed)
	print('Press Enter to Exit')
	input()
