#...............Importing important functionalities...................
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.user import User
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
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
                "Welcome !.."+full_name+"\nThank you for visiting me."+"\nI am a telegram bot."+
                "\nyou just send me the name of movie, webseries or TV Series and I Can give you the ratings and other details about the same. Thus you can decide whether "+
                "it is worth of watching or not..")

        def message_reply(update: Update, context: CallbackContext):
            suggest = suggestions.movie_scrapper(update.message.text, 'cinematerial')
            buttons = []
            for i in range(len(suggest)):
                buttons.append([KeyboardButton(suggest[i]['name']+'/'+str(suggest[i]['year']), request_contact = True, request_location = True)])
                
            buttons = ReplyKeyboardMarkup(buttons)
            update.message.reply_text(text = 'Hi', reply_markup = buttons)

            """re_dict = movie_rating.movieRating(update.message.text)
            reslt = '\n'
            for ky in re_dict.keys():
                    if ky == 'ygd':
                        reslt += re_dict[ky] + '\n\n'
                    else:   
                        reslt += ky + ' : ' + re_dict[ky] + '\n\n'
            if len(re_dict) != 0:
                    update.message.reply_text(reslt)
                    return 1
            update.message.reply_text("Could not find the exact match !\n"+
                                      "Try adding 'movie', 'webseries' etc. in your search..\n"+
                                      "Ex. 'Gravity movie' or 'Vikings webseries' ")"""    
                
                
           
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, message_reply))  
    
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
        return "Hello World !"
            
    return render_template("new_line_string.html")
    
if __name__ == '__main__':
    set_bot()
    app.run()

	
