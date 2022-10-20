#...............Importing important functionalities...................
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.user import User
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
import requests
import logging
import json
import time
import threading
import os
import codecs
import manage_db as db

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
            

        def keyboard_query(update: Update, context: CallbackContext):
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
                
                
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, get_suggestions))
        updater.dispatcher.add_handler(CallbackQueryHandler(keyboard_query))
    
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
                              webhook_url = https_url+':443/'+bot_token, allowed_updates = ["callback_query", "message"])
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

	
