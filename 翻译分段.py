#! python3
# -*- coding: utf-8 -*-
#本脚本在python 3.6下开发，请使用python 3运行
#win&GNU/Linux请用管理员权限安装pyperclip模块
#win: 以管理员权限运行命令提示符 (win+x, a; 或在开始菜单搜索cmd.exe右键管理员权限运行)
#然后输入py -3 -m pip install pyperclip回车
#GNU/Linux: 首先确认是否有pip, 没有的话安装 https://packaging.python.org/install_requirements_linux/#installing-pip-setuptools-wheel-with-linux-package-managers
#然后在Terminal中python3 -m pip install pyperclip
import pyperclip
while True:
	parse = input('[offsetSec+]min:sec,people\n')
	curPos = parse.find('+')
	if curPos == -1:
		offsetSec = 0
	else:
		offsetSec = int(parse[:curPos])
		parse = parse[curPos+1:]
	
	curPos = parse.find(':')
	totalMin = int(parse[:curPos])
	parse = parse[curPos+1:]
	
	curPos = parse.find(',')
	if curPos == -1:
		totalSec = int(parse)
		people = 1
	else:
		totalSec = int(parse[:curPos])
		parse = parse[curPos+1:].strip()
		people = int(parse)
	
	s = ''
	min = [offsetSec // 60]
	sec = [offsetSec % 60]
	intervalSec = (totalMin * 60.0 + totalSec - offsetSec)  / people
	for x in range (0, people):
		sec.append(sec[-1] + intervalSec)
	for x in range (1, people + 1):
		min.append(int(sec[x] / 60))
		sec[x] = round(sec[x] % 60)
	for x in range (0, people):
		s += '//%02d:%02d-%02d:%02d @初翻\n' %(min[x], sec[x], min[x+1], sec[x+1])
	print(s)
	#copyFlag = raw_input('Copy to clipboard? (Y/N)')
	#if (len(copyFlag) >0 and copyFlag[0].lower() == 'y'):
	pyperclip.copy(s)
	print('Copied to clipboard')