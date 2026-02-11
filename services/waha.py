import requests


class Waha:

    def __init__(self):
        self.__api_url = 'http://waha:3000'
        self.__api_url = 'http://localhost:3000'

    def send_message(self, chat_id, message):
        url = f'{self.__api_url}/api/sendText'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': 'default',
            'chatId': chat_id,
            'text': message,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )

    def get_history_messages(self, chat_id, limit):
        url = f'{self.__api_url}/api/default/chats/{chat_id}/messages?limit={limit}&downloadMedia=false'
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.get(
            url=url,
            headers=headers,
        )

        sorted_history = sorted(response.json(), key=lambda x: x['timestamp'])
        conversation = []
        for msg in sorted_history:
            sender = "Chatbot" if msg['fromMe'] else "User"
            #sender = "ai" if msg['fromMe'] else "human"
            conversation.append(f"{sender}: {msg['body']} -{msg['timestamp']}")
            #sender = "ai" if msg['fromMe'] else "human"
            #conversation.append(f"type: {sender}, content: {msg['body']}")

        return '\n'.join(conversation[:-1])

    def get_user_message(self, chat_id, limit=1):
        url = f'{self.__api_url}/api/default/chats/{chat_id}/messages?limit={limit}&downloadMedia=false'
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.get(
            url=url,
            headers=headers,
        )

        sorted_history = sorted(response.json(), key=lambda x: x['timestamp'])
        conversation = []
        for msg in sorted_history:
           if msg['fromMe'] == False:
            conversation.append(f"{msg['body']}")
            
        return conversation
    def start_typing(self, chat_id):
        url = f'{self.__api_url}/api/startTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': 'default',
            'chatId': chat_id,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )

    def stop_typing(self, chat_id):
        url = f'{self.__api_url}/api/stopTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': 'default',
            'chatId': chat_id,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )