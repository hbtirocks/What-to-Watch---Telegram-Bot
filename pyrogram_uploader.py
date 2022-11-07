from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from urllib.parse import unquote
import requests
import math
import os
import time

app = Client(name = 'URL UPLOADER', api_id = 23973455, api_hash = '1869935ebff7c985ae673d1b1ef4c550')

class CustomError(Exception):
    pass

def file_size(sib):#sib-size in bytes
    if sib < 0:
        raise CustomError('Value Error : File size can not be negative')
    notation = ['B', 'KB', 'MB', 'GB', 'TB']
    if sib >= 1:
        indx = int(math.floor(math.log(sib, 1024)))
        size = round(sib/math.pow(1024, indx),2)
        return f'{size} {notation[indx]}'
    else:
        return f'{sib} {notation[0]}'
    
def cal_time(sec):
    if sec<0:
        raise CustomError('Value Error : Time can not be negative')
    delta = {}
    delta['sec'] = sec%60
    sec -= delta['sec']
    if sec>0:
        delta['min'] = int(sec/60)%60
        sec -= delta['min']*60
    if sec>0:
        delta['hours'] = int(int(sec/60)/60)%24
        sec -= delta['hours']*60*60
    if sec>0:
        delta['days'] = int(int(int(sec/60)/60)/24)
    
    symbol = ['days', 'hours', 'min', 'sec']
    time_str = ''
    for i in range(len(symbol)):
        if delta.get(symbol[i], -1)>=0:
            time_str += f'{delta[symbol[i]]:02d} {symbol[i]} '
    return time_str
    
def download_progress(req, file_name, message, reply):
    if os.path.isfile('tmp\\'+file_name):
        os.remove('tmp\\'+file_name)
    sib = int(req.headers['content-length'])
    t_size = file_size(sib)
    dw_file = open('tmp\\'+file_name, 'ab')
    t0 = time.time()
    t1 = time.time()
    s1 = os.stat('tmp\\'+file_name).st_size
    for chunk in req.iter_content(chunk_size = 1024):
        dw_file.write(chunk)
        t2 = time.time()
        dt = t2-t1
        if dt > 1:
            s2 = os.stat('tmp\\'+file_name).st_size
            speed = file_size(int((s2-s1)/dt))
            prcntg = round(s2*100/sib, 2)
            bar = '['+''.ljust(int(0.2*prcntg), '⦿')+''.rjust(20-int(0.2*prcntg), '⦾')+']'
            etd = cal_time(int((sib-s2)*dt/(s2-s1)))
            reply.edit('<b><i>Downloading...\n</i></b><b>File Name :</b> <code>{0}\n</code><b>Done :</b> <i>{1} of {2}\n</i><b>Speed :</b> <i>{3}/s\n</i><b>Percentage :</b> <i>{4} %\n</i><b>Time Elapsed :</b> <i>{5}\n</i><b>ETD :</b> <i>{6}\n</i>{7}'.format(file_name, file_size(s2), t_size, speed, prcntg, cal_time(int(t2-t0)), etd, bar))
            t1 = t2
            s1 = s2
    dw_file.close()
    process_file(file_name, message, reply)
    if os.path.isfile('tmp\\'+file_name):
        os.remove('tmp\\'+file_name)

      
def process_file(file_name, message, reply):      
    #Uploading file to telegram database.
    reply.edit('<b><i>Processing...</i></b>')
    global t0, t1, s1
    t0 = time.time()
    t1 = time.time()
    s1 = 0
    uploaded_file = message.reply_video(video = 'tmp\\'+file_name, supports_streaming = True, progress = upload_progress, progress_args = (reply, file_name, t1))
    reply.delete()

    
            
def upload_progress(uploaded, total, *args):
            global t0, t1, s1
            t2 = time.time()
            s2 = uploaded
            speed = file_size(int((s2-s1)/(t2-t1)))
            prcntg = round(s2*100/total, 2)
            print(prcntg)
            bar = '['+''.ljust(int(0.2*prcntg), '⦿')+''.rjust(20-int(0.2*prcntg), '⦾')+']'
            etd = cal_time(int((total-s2)*(t2-t1)/(s2-s1)))
            args[0].edit('<b><i>Uploading as streamble video...\n</i></b><b>File Name :</b> <code>{0}\n</code><b>Done :</b> <i>{1} of {2}\n</i><b>Speed :</b> <i>{3}/s\n</i><b>Percentage :</b> <i>{4} %\n</i><b>Time Elapsed :</b> <i>{5}\n</i><b>ETD :</b> <i>{6}\n</i>{7}'.format(args[1], file_size(s2), file_size(total), speed, prcntg, cal_time(int(t2-t0)), etd, bar))
            t1 = t2
            s1 = s2
            
@app.on_message()
def url_loader(client, message):
    reply = message.reply('<b><i>Processing...</i></b>', quote = True)
    url = message.text
    file_name = unquote(url.split('/').pop())
    #extracting File Name from encoded url
    txt = '<b>🕹 Choose what you want to do with this file..\n</b>'
    txt += '<code>File Name : {0}\n'.format(file_name)
    req = requests.get(url = message.text, stream = True)
    size = file_size(int(req.headers['content-length']))
    txt += 'File Size : {0}\n'.format(size)
    txt += 'File Type : {0}\n</code>'.format(req.headers['content-type'])
    formats = {'video' : 'mp4 mkv 3gp flv wmv mov avi webm', 'audio' : 'pcm wav aiff mp3 aac wma flac alac ogg', 'image' : 'jpeg jpg png gif svg tiff tif bmp webp psd eps ai indd'}
    #collection of most used video/audio/image formats
    file_type = 'document'
    for ky in formats.keys():
        if formats[ky].find(file_name.split('.').pop().lower()) != -1:
            file_type = ky
            break
    #getting File Type by checking File Name against formats
    btns = ('Document', 'Video', 'Audio', 'Image', 'Screenshots', 'Trim', 'Resize', 'Close')
    emoji = ('📄 ','📹 ', '🔊 ', '🛤 ', '📷 ', '✂️ ', '↔️ ', '✖️ ')
    #collection of InlineKeyboardButton for all file types
    slctd = {'document' : '0 7', 'video' : '0 1 4 5 7', 'audio' : '0 2 5 7', 'image' : '0 3 6 7'}
    #InlineKeyboardButton selection based on file_type
    blist = slctd[file_type].split(' ')
    #list of selected buttons
    optns = [] #buttons to be sent with message_reply
    for i in range(0, len(blist), 2):
        optns.append([InlineKeyboardButton(text = emoji[int(blist[i])]+btns[int(blist[i])], callback_data = btns[int(blist[i])])])
        if i+1 < len(blist):
            optns[len(optns)-1].append(InlineKeyboardButton(text = emoji[int(blist[i+1])]+btns[int(blist[i+1])], callback_data = btns[int(blist[i+1])]))

    if req.status_code == 200:
        reply.edit(text = txt, reply_markup = InlineKeyboardMarkup(optns))
        download_progress(req, file_name, message, reply)        
    else:
        reply.edit(f"<i><b>Error:</b></i> <code>{req.status_code} {req.reason}</code>")
    
app.run()
