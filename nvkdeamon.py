#! python3
# -*- coding: utf-8 -*-
'''
自动监测生肉文件夹变化，如果有新文件进入自动启动压制
'''

import sys
def show_exception_and_exit(exc_type, exc_value, tb):
	import traceback
	traceback.print_exception(exc_type, exc_value, tb)
	input('''脚本遇到错误，请截图此画面发送给Kilo19。5秒后继续
	Error encountered, please send a screenshot of this error to Kilo19
	Press Enter to Exit
	''')
	import time
	time.sleep(5)

sys.excepthook = show_exception_and_exit

import subprocess
import codecs
import time
import sys
import os
import nvksupport
from settings import cloudRoot, cloudDir, customDownDir

scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))

def GrabArgs(lines, argLen):
	returnVal = [''] * argLen
	for x in range(len(returnVal)):
		if len(lines) > x:
			returnVal[x] = lines[x].strip()
	return returnVal

def ListIngredients(dirPath, name, ext):
	myIngredients = set()
	if os.path.isdir(dirPath):
		for root, dirs, files in os.walk(dirPath):
			if root == dirPath:
				for file in files:
					if not name in file and file[-3:] == ext:
						fileStr = os.path.join(root, file) + '\n'
						myIngredients.add(fileStr)
	return myIngredients

def ListFile(dirPath, name, ext):
	candidates = set()
	if os.path.isdir(dirPath):
		for root, dirs, files in os.walk(dirPath):
			for file in files:
				if file[-3:] == ext and name in file:
					fileStr = os.path.join(root, file) + '\n'
					candidates.add(fileStr)
	return candidates

def SafeReadandWriteHead(inName, fileHead = None):
	lines = []
	if not os.path.isfile(inName):
		codecs.open(inName, 'w', 'utf-8').close()
	else:
		inf = codecs.open(inName, 'r', 'utf-8')
		lines = inf.readlines()
		inf.close()

	lines = [line.strip() + '\n' for line in lines]
	if fileHead:
		fileHead = [l.strip() + '\n' for l in fileHead]
		if len(lines) < len(fileHead) or lines[:len(fileHead)] != fileHead:
			print("writehead: " + time.ctime())
			inf = codecs.open(inName, 'w', 'utf-8')
			inf.writelines(fileHead)
			inf.close()
	x = 0
	while x < len(lines):
		if lines[x][0] == '#':
			lines.pop(x)
		else:
			x += 1
	return lines

def DeamonHelper(inName, argLen, scriptName, fileHead):
	inName = os.path.join(customDownDir, inName + '.txt')
	lines = SafeReadandWriteHead(inName, fileHead)
	if len(lines):
		inf = codecs.open(inName, 'w+', 'utf-8')
		if fileHead:
			fileHead = [l.strip() + '\n' for l in fileHead]
			inf.writelines(fileHead)
		else:
			inf.write('')
		inf.close()

		while lines:
			args = GrabArgs(lines, argLen)
			lines = lines[len(args):]
			print(inName + ' command: ' + time.ctime())
			for arg in args:
				print(arg)
			# For safety
			time.sleep(0.5)
			subprocess.Popen(
				[
					'py', '-3', os.path.join(scriptDir, scriptName + '.py')
				] + args,
				creationflags = subprocess.CREATE_NEW_CONSOLE
			 )

if __name__ == "__main__":
	print("NVK Deamon online: " + time.ctime())
	ingHead = ['#网盘高压下令文件',
			'#不要删除开头带#的行，这些都是注释',
			'#不要使用OC网页版编辑此文件',
			'#此文件为UTF-8编码，用来下令压生肉',
			'#下令前请先用everything搜索（任务栏那个放大镜）',
			'#优先下载1080p',
			'#搜索时按Alt+3然后Alt+4可以缩放everything窗口',
			'#生肉速度大约视频1/2时长',
			'#同步到网盘速度不等']

	beHead = ['#压熟肉下令文件，带#的行都是注释',
			'#请在BUG检测完成后再压制',
			'#不要使用OC网页版编辑此文件',
			'#教程https://docs.google.com/document/d/1CdyqEP7eanL6J6xUpbcOuq-uIBQkSEqhhHgeGFT94ik/edit',
			'#此文件为UTF-8编码，用来下令压熟肉',
			'#熟肉速度大约视频0.8-0.9倍',
			'#请同时提供生肉路径与字幕所在网盘文件夹，然后保存',
			'#同步到网盘速度不等']

	cookedHead = ['#此文件专门记录熟肉路径，自动更新',
			   '#请优先从已有熟肉中选择上传',
			   '#上传完成后尽快删除']

	while True:
		DeamonHelper("ing", 1, "NixieCloud_Enc", ingHead)
		DeamonHelper("BE", 3, "Bili_Enc", beHead)

		ingredientsListPath = os.path.join(
			scriptDir, 'ingredientsList' + '.txt'
		)
		ingredients = ListIngredients(customDownDir, '[BE_', 'mp4')

		cookedPath = os.path.join(customDownDir, 'cookedList' + '.txt')
		cooked = ListFile(os.path.join(cloudRoot, cloudDir), '[BE_', 'mp4')

		oldIngList = set(SafeReadandWriteHead(ingredientsListPath, None))
		oldcookedList = set(SafeReadandWriteHead(cookedPath, None))

		if ingredients != oldIngList:
			#set difference finds new ingredients to transcode
			newIngs = list(ingredients - oldIngList)
			print('Auto NCE: ' + time.ctime())
			for newIng in newIngs:
				print(newIng)
				newIngStripped = newIng.strip()
				newIngStripped = nvksupport.ReplaceNaughtyCharacters(
					newIngStripped, nvksupport.tl
				)
				subprocess.Popen(
					[
						'py', '-3',
						os.path.join(scriptDir, "NixieCloud_Enc" + '.py'),
						newIngStripped
					],
					creationflags=subprocess.CREATE_NEW_CONSOLE
				)
			ingredients = ListIngredients(customDownDir, '[BE_', 'mp4')
			print("writeIng: " + time.ctime())
			outFile = codecs.open(ingredientsListPath, 'w', 'utf-8')
			outFile.writelines(list(ingredients))
			outFile.close()

		if cooked != oldcookedList:
			print("writeCooked: " + time.ctime())
			codecs.open(cookedPath, 'w', 'utf-8').close()
			SafeReadandWriteHead(cookedPath, cookedHead)
			outFile = codecs.open(cookedPath, 'a+', 'utf-8')
			outFile.writelines(list(cooked))
			outFile.close()

		time.sleep(5)
