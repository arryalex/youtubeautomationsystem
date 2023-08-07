import os 
import telebot

def Send_Notification(Original_link, Uploade_link,Original_title, Channel_from):
    API_KEY = '6187555524:AAHRWR0RJUOmFackmbeEZtcejMHp9CEeM50'
    template = f'''
<a href="https://www.youtube.com/watch?v={Uploade_link}"><i>Hurry Up Shorts Oficial Just Upload A Video</i></a>
<s><i>Original Link - {Original_link}  </i></s>
<s><i>Original Title - {Original_title} </i></s>
<u><i>Channel From - {Channel_from}</i></u>
    '''
    bot = telebot.TeleBot(API_KEY)
    request = bot.send_message(chat_id=1518832426,text=template, parse_mode='html')
    print(request)

