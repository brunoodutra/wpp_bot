import os

from decouple import config

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

from langchain.callbacks.manager import CallbackManager

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')


class AIBot:

    def __init__(self):
        self.__LLM1 = ChatGroq(model='llama-3.3-70b-versatile')
        self.__LLM2 = ChatGroq(model='moonshotai/kimi-k2-instruct-0905')
        #self.__chat = Ollama(model="lllama3.2:latest",callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

        #self.__retriever = self.__build_retriever()
    def format_history(self, history):

        # Estrutura do prompt
        prompt = PromptTemplate(
            input_variables=['chat_history'],
            template='''
                System:
                  
                Você é responsável por analisar um histórico de conversas médicas entre um chatbot e um usuário. Determine o tipo de conversa (nova, recente ou continuação) e detecte se o **assunto mudou** com base nos seguintes critérios:

                ### Classificação:
                1. **Nova Conversa**:
                - Quando há uma diferença de timestamps significativa (ex.: >3600 segundos entre o último e o penúltimo item).
                - Ou a conversa inicia com saudações como: "Bom dia", "Boa tarde", "Oi", "Olá", etc.
                - Retorne um histórico vazio: `[]`.

                2. **Conversa Recente**:
                - Quando a diferença de timestamps é pequena (ex.: <=3600 segundos) e o assunto parece ser novo, mas relacionado à interação anterior. 
                - Retorne apenas as 3 últimas interações no formato:
                    ```
                    User: [mensagem do usuário] 
                    Chatbot: [resposta do chatbot]
                    ```

                3. **Continuação de Conversa**:
                - Se a conversa continua o mesmo assunto ou tema do histórico anterior.
                - Retorne um resumo relevante do histórico no formato:
                    ```
                    User: [mensagem do usuário]
                    Chatbot: [resposta do chatbot] 
                    ```

                4. **Mudança de Assunto**:
                - Identifique se o tópico mudou. O assunto é considerado diferente se:
                    - O usuário introduz novos sintomas, doenças, medicamentos ou tópicos médicos que não têm relação direta com as mensagens anteriores.
                    - A conversa inclui palavras ou expressões como: "Agora falando de outra coisa", "Mudando de assunto", etc.
                    - Uma saudação aparece no meio do histórico.
                - Retorne apenas as interações relevantes ao novo tópico, ignorando o restante do histórico.

                **Formato do Histórico**:
                - Cada interação deve ser estruturada como:
                ```
                User: [mensagem do usuário] 
                Chatbot: [resposta do chatbot] 
                ```

                History:
                {chat_history}

                Responda apenas com o histórico formatado, sem outros detalhes ou explicações.

                Formated_History:
            '''
        )

        # Encadeando o prompt com o modelo
        self.chain_history_manage = LLMChain(llm=self.__LLM2, prompt=prompt, verbose=True)
        response = self.chain_history_manage.run(chat_history=history)

        return response

    def invoke(self, question, history = None):
        # Verificando se a pergunta foi passada corretamente

        user_question = question[-1]

        # Estrutura de Few-Shot Examples: Exemplos de como o modelo deve responder
        few_shot_examples = [
            ("Quem é você?", "Sou o chatbot virtual de diagnóstico médico, posso tirar dúvidas sobre sintomas, doenças e medicamentos. Como posso ajudar?"),
            ("O que você faz?", "Posso tirar dúvidas sobre sintomas, doenças e medicamentos. Como posso ajudar?"),
            ("O que é pneumonia?", "Pneumonia é uma infecção pulmonar que pode ser causada por bactérias, vírus ou fungos. Você está com sintomas como febre, tosse ou dificuldade para respirar?"),
            ("Quais exames são feitos para diagnosticar anemia?", "Os exames mais comuns para diagnosticar anemia incluem o hemograma completo e, em alguns casos, dosagens de ferro sérico e ferritina. Algum médico já recomendou esses exames?"),
            ("Qual é o próximo jogo do time X?", "Desculpe, só posso responder perguntas relacionadas a medicina e saúde."),
            ("What is the best medicine for flu?", "Por favor, reformule sua pergunta em Português. Sou treinado para responder apenas em Português."),
            ("Estou com dor no peito.", "Dor no peito pode ter várias causas. É uma dor constante, ou aparece em momentos específicos, como ao se movimen9tar ou respirar fundo?"),
            ("to com dor", "Me fale mais sobre essar dor, em que parte do corpo você está sentindo dor ?"),
            ("to com febre", "A febre pode ter várias causas, como infecções, inflamações ou outras condições subjacentes. É importante consultar um médico para um diagnóstico preciso e tratamento adequado. Você tem algum outro sintoma, como dor de cabeça, náusea ou dor muscular?"),
            ("Quem te criou? Quem é seu criador?", "Meu criador é o PhD Bruno Dutra. Contato: https://www.linkedin.com/in/bruno-gomes-dutra-phd-28aa56104/")
        ]
        
        # Concatenando os exemplos de Few-Shot com a pergunta do usuário
        few_shot_prompt = ""
        for example in few_shot_examples:
            few_shot_prompt += f"User:{example[0]}\nChatbot:{example[1]}\n"

        # Estrutura do prompt
        prompt = PromptTemplate(
            input_variables=['user_text', 'few_shot', 'chat_history'],
            template='''
            System:

            "Você é um chatbot de diagnóstico médico." 
            "Seu objetivo é auxiliar médicos, profissionais de saúde e pacientes analisando as informações fornecidas e fornecer uma resposta conclusiva depois de entender o contexto geral da convesa."
            "Siga estas diretrizes:\n"
            "- Responda exclusivamente em Português. Nunca responda em outro idioma.\n"
            "- Responda apenas perguntas relacionadas a sintomas, diagnósticos, informações medicinais, possíveis tratamentos, exames complementares, orientações iniciais ou sobre seu objetivo e diretrizes.\n"
            "- Antes de fornecer uma resposta final, sempre pergunte por mais sintomas ou detalhes que possam ajudar a compreender melhor o quadro clínico."
            "- Ao concluir um diálogo ou perceber que o usuário não tem mais dúvidas, sempre pergunte se pode ajudar em algo mais.\n"
            "- Mesmo quando o mais indicado for procurar um médico, informe remédios ou métodos de atenuar os sintomas reportados.\n"
            "- Nunca informe que o usuário precisa consultar um médico para um diagnóstico preciso e tratamento adequado.

            Examples: [{few_shot}]

            History: [{chat_history}]
    
            User: {user_text}
    
            Chatbot:

            '''
        )

        # Encadeando o prompt com o modelo
        self.chatbot_chain = LLMChain(llm=self.__LLM1, prompt=prompt, verbose=True)
        response = self.chatbot_chain.run(user_text=user_question, few_shot=few_shot_prompt, chat_history=history)

        return response
        