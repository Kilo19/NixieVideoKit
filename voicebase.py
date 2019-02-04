#! python3
# -*- coding: utf-8 -*-
import nvksupport
import tempfile
import requests
import codecs
import random
import time
import json
import sys
import os
from settings import voicebaseToken

def pretty_print_POST(req):
	"""
	At this point it is completely built and ready
	to be fired; it is "prepared".

	However pay attention at the formatting used in 
	this function because it is programmed to be pretty 
	printed and may differ from the actual request.
	"""
	print('{}\n{}\n{}\n\n{}'.format(
		'-----------START-----------',
		req.method + ' ' + req.url,
		'\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
		req.body,
	))


def SubmitMedia(audioIn):
	url = 'https://apis.voicebase.com/v3/media'
	configuration = {
		'transcript':{
			'formatting':{
				'enableNumberFormatting':'true'
			}
		}
	}
	files = {'configuration': ('configuration.json', json.dumps(configuration), 'application/json'),
					'media': ('sample.mp3', open(audioIn, 'rb'), 'audio/mpeg')}
	headers = {'Authorization': 'Bearer ' + voicebaseToken}
	'''
	req = requests.Request('POST', url, headers=headers, files=files)
	prepared = req.prepare()
	pretty_print_POST(prepared)
	exit()
	'''
	r = requests.post(url, headers=headers, files=files)
	retJson = r.json()
	mediaId = retJson['mediaId']
	print(mediaId)
	return mediaId
	#return example: {'mediaId': 'ecdfbb91-bb5e-4315-b726-30693e4576a8', '_links': {'self': {'href': '/v2-beta/media/ecdfbb91-bb5e-4315-b726-30693e4576a8'}}, 'metadata': {}, 'status': 'accepted'}

def PollAndSpitJson(mediaId, outPath):
	outJsonPath = outPath + '.json'
	url = 'https://apis.voicebase.com/v3/media/%s' % mediaId
	headers = {'Authorization': 'Bearer ' + voicebaseToken}
	while True:
		r = requests.get(url, headers=headers)
		jsonObj = r.json()
		if jsonObj['media']['status'] != 'finished':
			print('File processing, current status:' + jsonObj['media']['status'])
			print('Next call in 10 seconds...')
			time.sleep(10)
		else:
			outJson = codecs.open(outJsonPath, 'w', 'utf-8')
			json.dump(jsonObj, outJson)
			outJson.close()
			print('Data written to ' + outJsonPath)
			return jsonObj
			
def SpitTranscriptFromJson(jsonIn, outPath):
	outTxtPath = outPath + '.txt'
	outTxt = codecs.open(outTxtPath, 'w', 'utf-8')

	data = jsonIn
	words = data["media"]["transcripts"]["latest"]["words"]
	outList = [words[0]['w']]
	
	for i in range(1, len(words)):
		if 'm' in words[i].keys():
			outList[-1] += '.'
		else:
			outList[-1] += ' '
			outList.append(words[i]['w'])
	
	outTxt.writelines(outList)
	outTxt.close()
	print('Transcript written to ' + outTxtPath)
	
if __name__ == '__main__':
	argLen = len(sys.argv)
	if argLen == 1:
		audioIn = input('drag Audio or sourceVideo here').replace('"', '')
		spitPath = os.path.splitext(audioIn)[0]
	elif argLen == 2:
		audioIn = sys.argv[1]
		spitPath = os.path.splitext(audioIn)[0]
		audioIn = audioIn.replace('"', '')
		spitPath = spitPath.replace('"', '')
	elif argLen > 2:
		audioIn = sys.argv[1]
		spitPath = sys.argv[2]

	audioIn = audioIn.replace('"', '')
	spitPath = spitPath.replace('"', '')
	if (audioIn[-4:] == 'json'):
		jsonPath = audioIn
		with codecs.open(jsonPath, encoding = 'utf-8') as jsonFile:
			SpitTranscriptFromJson(json.load(jsonFile), spitPath)
	else:
		temp = {}
		if audioIn[-4:] != '.mp3':
			sourceMedia_split = list(os.path.split(audioIn))
			sourceMedia_split[1:] = os.path.splitext(sourceMedia_split[1])
			tempDir = tempfile.gettempdir()
			serial = str(random.randint(0,255))
			tempName = sourceMedia_split[1] + serial
			temp['path'] = os.path.join(tempDir, tempName)
			#temp['path'] = os.path.join(tempDir, serial)
			temp['audio_path'] = temp['path'] + '_a' + '.mp3'
			scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
			libDir = os.path.join(scriptDir, 'Program')
			os.chdir(libDir)
			nvksupport.ConvertAudioVoicebase(audioIn, temp['audio_path'])
			audioIn = temp['audio_path']

		mediaId = SubmitMedia(audioIn)

		nvksupport.tempClean(temp)

		jsonObj = PollAndSpitJson(mediaId, spitPath)
		SpitTranscriptFromJson(jsonObj, spitPath)