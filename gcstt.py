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
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from google.cloud import storage

def generate_json(response):
    vbjson = {'transcript': {'words':[]}}
    position = 0
    for result in response.results:
        for word in result.alternatives[0].words:
            starttime = int(word.start_time.seconds*1000+word.start_time.nanos/1000000)
            endtime = int(word.end_time.seconds*1000+word.end_time.nanos/1000000)
            vbjson['transcript']['words'].append({'p':position,'s':starttime, 'c':word.confidence, 'e':endtime, 'w':word.word})
            position = position+1
    return vbjson

def speech_to_text(gcs_uri):
    #ltt_context = open('context.txt', 'r').read().split('\n')
    client = speech_v1p1beta1.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)
    #speech_contexts_element = {"phrases": ltt_context, "boost": 11}
    #speech_contexts = [speech_contexts_element]
    config = {
        "encoding": enums.RecognitionConfig.AudioEncoding.MP3,
        "sample_rate_hertz": 48000,
        "language_code": 'en-US',
        #"speech_contexts": speech_contexts,
        "max_alternatives": 11,
        "model": "video",
        "enable_word_confidence" : True,
        "enable_word_time_offsets" : True,
        "enable_automatic_punctuation": True
    }
    operation = client.long_running_recognize(config, audio)
    print('Speech-to-Text running.')
    response = operation.result()
    return(response)

def upload_to_gcs(audio_filename):
    basename = os.path.basename(audio_filename)
    storage_client = storage.Client()
    bucket_name = "nvkstt"
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        bucket = storage_client.create_bucket(bucket_name)
    blob = bucket.blob(basename)
    blob.upload_from_filename(audio_filename)
    gcs_uri = "gs://"+bucket_name+'/'+basename
    return (gcs_uri)

def clean_gcs(audio_filename):
    basename = os.path.basename(audio_filename)
    storage_client = storage.Client()
    bucket_name = "nvkstt"
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(basename)
    blob.delete()

def exec_transcribe(filename):
    response = speech_to_text(upload_to_gcs(filename))
    return generate_json(response)

def SpitTranscriptFromJson(jsonIn, outPath):
    outTxtPath = outPath + '.txt'
    outTxt = codecs.open(outTxtPath, 'w', 'utf-8')

    data = jsonIn
    words = data["transcript"]["words"]
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

def spitJson(mediaId, outPath):
    outJsonPath = outPath + '.json'
    outJson = codecs.open(outJsonPath, 'w', 'utf-8')
    json.dump(jsonObj, outJson)
    outJson.close()
    print('Data written to ' + outJsonPath)

    
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

        jsonObj = exec_transcribe(audioIn)
        nvksupport.tempClean(temp)

        spitJson(jsonObj, spitPath)
        SpitTranscriptFromJson(jsonObj, spitPath)