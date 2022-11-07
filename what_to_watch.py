#...............Importing important functionalities...................
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.user import User
from telegram.forcereply import ForceReply
#from telegram.message import Message
#from telegram.chat import Chat
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import movie_rating
import suggestions
from flask import Flask, request, render_template, send_file, send_from_directory
from flask_ngrok import run_with_ngrok
from urllib.parse import unquote
import requests
import logging
import json
import time
import threading
import os
import re
import manage_db as db
from url_uploader import download_progress, file_size

logging.basicConfig(level = logging.DEBUG)
bot_token = "5464528533:AAEdqNZaOwiNUot5-4ng6K1c0-YnuRHelhQ"

def set_bot():
    def deploy_bot():
        global updater
        updater = Updater(token = bot_token, use_context = True)

        def start(update: Update, context: CallbackContext):
            user = update.message.from_user
            full_name = user.first_name
            if user.last_name != None:
                full_name += ' '+user.last_name
            update.message.reply_text(
                "<b><i>Welcome  ‼..</i></b><u>"+full_name+"</u>\n<i>Thank you for visiting me..🙏</i>"+"\n<i>I am a telegram bot..🤖</i>\n"+
                "\n<b><i>Things I can do for you:-</i></b>\n"+
                "\n1. <i>you just send me the name of movie  🎬, webseries  🎞 or TV Series  📺 and I Can give you the ratings  🎖 and other details  📝 about the same. Thus you can decide whether </i>"+
                "<i>it is worth of watching  🕶 or not..\n\n Ex.-For a movie 'Dil Bechara'..\nSend the message like:- Dil or Dil Bechara\n</i>"+
                "\n<b>Additional features - soon to be added..‼</b>", parse_mode = 'html')

        def get_suggestions(update: Update, context: CallbackContext):
            temp_msg = update.message.reply_text('🆂🅴🅰🆁🅲🅷🅸🅽🅶...🔎')
            suggest = suggestions.movie_scrapper(update.message.text)
            txt = ''
            option = []
            for i in range(len(suggest)):
                txt += '<i>\n{0}. {1}\n  Year:-{2}\n  Category:-{3}\n</i>'.format(i+1, suggest[i]['name'], suggest[i]['year'], suggest[i]['catgry'])
                option.append(InlineKeyboardButton(text = i+1, callback_data = i))
            txt += '<i>\nNone of the results matching your search..\nTry again with more precise words..\n\n</i><b><i>Choose your option and press the button below..</i></b>'
                
            temp_msg.delete()
            sent_msg = update.message.reply_text('<b><i>Results matching your search...</i></b>\n'+txt, reply_markup = InlineKeyboardMarkup([option]), parse_mode = 'html')

            #Updating database
            values = []#values to be passed to database
            for i in range(len(suggest)):
                values.append((sent_msg.chat.id, sent_msg.message_id, i, suggest[i]['name'], suggest[i]['year'], suggest[i]['catgry'], suggest[i]['poster']))
            db.write_table('movie_info.db', 'chat_info', 'INSERT', values = values)
            

        def movie_query(update: Update, context: CallbackContext):
            qry = update.callback_query
            temp_msg = qry.message.reply_text("🅵🅴🆃🅲🅷🅸🅽🅶 🅸🅽🅵🅾...ℹ")
            slctd_mv = db.read_table('movie_info.db', 'chat_info', select = ['name', 'year', 'category', 'poster'],
                                 where = ['chat_id', 'and', 'message_id', 'and', 'id'], values = (qry.message.chat.id, qry.message.message_id, qry.data))
            #slctd_mv :- selected movie by telegram user.
            
            if len(slctd_mv):
                re_dict = movie_rating.movie_overview(slctd_mv[0])
                poster = re_dict['poster']
                del re_dict['poster']
                reslt = '\n'
                for ky in re_dict.keys():
                        if ky == 'ygd' or ky == 'ratings':
                            reslt += '<i>{0}\n</i>'.format(re_dict[ky])
                        else:
                            if ky == 'Title':
                                reslt += '<i><b>{0} : {1}\n\n</b></i>'.format(ky, re_dict[ky])
                            else:
                                reslt += '<i>{0} : {1}\n\n</i>'.format(ky, re_dict[ky])
                if len(re_dict) != 0:
                        updater.bot.delete_message(qry.message.chat.id, qry.message.message_id)
                        temp_msg.delete()
                        
                        qry.message.reply_photo(photo = poster, caption = reslt, parse_mode = 'html')
                        db.write_table('movie_info.db', 'chat_info', 'DELETE', where = ['chat_id', 'and', 'message_id'], values = [(qry.message.chat.id, qry.message.message_id)])
                        return 1
                qry.message.reply_text("Could not find the exact match !\n"+
                                          "Try adding 'movie', 'webseries' etc. in your search..\n"+
                                          "Ex. 'Gravity movie' or 'Vikings webseries' ")

        #..............Code for uploading file from url link to telegram database...........
        def url_loader(update: Update, context: CallbackContext):
            reply = update.message.reply_text('<b><i>Processing...</i></b>', parse_mode = 'html', quote = True)
            url = update.message.text
            file_name = unquote(url.split('/').pop())
            #extracting File Name from encoded url
            txt = '<b>🕹 Choose what you want to do with this file..\n</b>'
            txt += '<code>File Name : {0}\n'.format(file_name)
            req = requests.get(url = url, stream = True)
            size = file_size(int(req.headers['content-length']))
            txt += 'File Size : {0}\n'.format(size)
            #.................Finding File Type...................
            formats = {'video' : 'mp4 mkv 3gp flv wmv mov avi webm', 'audio' : 'pcm wav aiff mp3 aac wma flac alac ogg', 'image' : 'jpeg jpg png gif svg tiff tif bmp webp psd eps ai indd'}
            #collection of most used video/audio/image formats
            file_type = 'document'
            for ky in formats.keys():
                if formats[ky].find(file_name.split('.').pop().lower()) != -1:
                    file_type = ky
                    txt += 'File Type : {0}\n</code>'.format(ky+'/'+file_name.split('.').pop().lower())
                    break
            #getting File Type by checking File Name against formats
            

            #..................Setting Up reply_markup buttons................
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
                reply.edit_text(text = txt, parse_mode = 'html', reply_markup = InlineKeyboardMarkup(optns))        
            else:
                reply.edit(text = f"<i><b>Error:</b></i> <code>{req.status_code} {req.reason}</code>", parse_mode = 'html')

            #Updating file_info table
            db.write_table('url_info.db', 'file_info', 'INSERT', values = [(update.message.chat.id, update.message.message_id, file_name),])

        def url_query(update: Update, context: CallbackContext):
            qry = update.callback_query
            if qry.data == 'Close':
                qry.message.delete()
            elif qry.data == 'Resize':
                pass
            elif qry.data == 'Trim':
                pass
            elif qry.data == 'Screenshots':
                pass
            else:
                qry.message.edit_reply_markup(reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = '📄 Default', callback_data = 'Default'), InlineKeyboardButton(text = '✏ Rename', callback_data = 'Rename')]]))
 
        def file_query(update: Update, context: CallbackContext):
            qry = update.callback_query
            qry.message.edit_text(text = '<i><b>Trying to download...</b></i>', parse_mode = 'html')
            if qry.data == 'Default':
                original_msg = qry.message.reply_to_message
                url = original_msg.text
                file_name = unquote(original_msg.text.split('/').pop())
                req = requests.get(url = url, stream = True)
                download_progress(req, file_name, original_msg, qry.message)
            else:
                original_msg = qry.message.reply_to_message
                file_name = unquote(original_msg.text.split('/').pop())
                qry.message.delete()
                original_msg.reply_text(text = f'<b>File Name: </b><code>{file_name}\n\n</code><i>Send new name for this file...</i>', quote = True, parse_mode = 'html', reply_markup = ForceReply(input_field_placeholder = 'Enter File Name..'))

        def download_after_rename(update: Update, context: CallbackContext):
            original_msg = update.message.reply_to_message
            reply = original_msg.reply_text(text = '<i><b>Trying to download...</b></i>', parse_mode = 'html')
            url = original_msg.text
            file_name = update.message.text
            req = requests.get(url = url, stream = True)
            download_progress(req, file_name, original_msg, reply)
            
            
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(MessageHandler(Filters.entity('url'), url_loader))
        updater.dispatcher.add_handler(MessageHandler(Filters.reply, download_after_rename))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, get_suggestions))
        updater.dispatcher.add_handler(CallbackQueryHandler(callback = movie_query, pattern = '[1-9]'))
        updater.dispatcher.add_handler(CallbackQueryHandler(callback = url_query, pattern = 'Doc|Vid|Aud|Ima|Scr|Tri|Res|Clo'))
        updater.dispatcher.add_handler(CallbackQueryHandler(callback = file_query, pattern = 'Def|Ren'))
    
        https_url = ''
        while https_url == '':
            url = "http://127.0.0.1:4040/api/tunnels/"
            try:
                req = requests.get(url)
                if req.status_code == 200:
                    req_unicode = req.content.decode("utf-8")
                    req_json = json.loads(req_unicode)
                    lst = req_json["tunnels"]
                    for i in range(len(lst)):
                        if lst[i]["proto"] == "https":
                            https_url = lst[i]["public_url"]
                            break
            except:
                print("server not started yet !")
            time.sleep(2)
        PORT = int(os.environ.get('PORT', '5000'))
        updater.start_webhook(listen = '0.0.0.0', port = PORT, url_path = bot_token,
                              webhook_url = https_url+':443/'+bot_token, drop_pending_updates = True, allowed_updates = ["callback_query", "message"])
        #print(updater.bot.getWebhookInfo().to_dict())
    thread = threading.Thread(target = deploy_bot)
    thread.start()


app = Flask(__name__)
run_with_ngrok(app)

@app.route("/"+bot_token, methods=["POST"])
def handle_webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), updater.bot)
        updater.dispatcher.process_update(update)
        return "Hello World!"
            
    return render_template("new_line_string.html")
    
if __name__ == '__main__':
    set_bot()
    app.run()

	
