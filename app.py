from flask import Flask, request, jsonify

from services.waha import Waha

#from bot.ai_bot_v1 import AIBot
from bot.ai_bot_v1 import AIBot

app = Flask(__name__)

@app.route('/chatbot/webhook/', methods = ['POST']) # route and method 
def webhook():

    waha = Waha()
    ai_bot = AIBot()

    data = request.json
    #print(f'=================================')
    #print(f'Received Event: {data}')
    #print(f'=================================')

    chat_id = data['payload']['from']

    if chat_id == '559180331035@c.us' or chat_id == "559193008090-1438136884@g.us" or chat_id == '551281087761@c.us' or chat_id == '559198105888@c.us' or chat_id == '559188190903@c.us'or chat_id == '559199422580@c.us':
    #print(f'Received Event: {data}')
        waha.start_typing(chat_id=chat_id)

        chat_history=waha.get_history_messages(chat_id, limit=30)
        user_query=waha.get_user_message(chat_id)
        #print(f'=================================')
        #print('>>>>>>>>>>>>>>>',user_query)
        #print(f'=================================')
        formated_history=ai_bot.format_history(history=chat_history)
        #print('>>>>>>>>>>>>>>>',formated_history)
        bot_message=ai_bot.invoke(question=user_query, history=formated_history )
        
        waha.send_message( 
            chat_id=chat_id, 
            message= bot_message)

        waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    print(f'Initing bot API...')
    app.run(host='0.0.0.0', port=5000, debug=True)