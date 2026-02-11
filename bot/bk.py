import os

from decouple import config

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_groq import ChatGroq

from langchain.callbacks.manager import CallbackManager

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')


class AIBot:

    def __init__(self):
        self.__chat = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview')

        #self.__chat = Ollama(model="lllama3.2:latest",callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

        #self.__retriever = self.__build_retriever()

    def invoke(self, question):
        # Verificar a entrada e separar histórico e a última pergunta
        user_question = question[-1]
        history = question[:-1] if len(question) > 1 else []

        # Exemplos Few-Shot
        few_shot_examples = [
            # Perguntas fora do escopo
            (HumanMessage(content="Qual é o próximo jogo do time X?"), AIMessage(content="Desculpe, só posso responder perguntas relacionadas a medicina e saúde.")),

            # Respostas em inglês (prevenção)
            (HumanMessage(content="What is the best medicine for flu?"), AIMessage(content="Por favor, reformule sua pergunta em Português. Sou treinado para responder apenas em Português.")),

            # Diálogos contínuos
            (HumanMessage(content="Estou com dor no peito"), AIMessage(content="Dor no peito pode ter várias causas. É uma dor constante, ou aparece em momentos específicos, como ao se movimentar ou respirar fundo?"))
            (HumanMessage(content="movimentar"), AIMessage(content="Entendi. Você apresenta catarro também ?"))
            (HumanMessage(content="sim"), AIMessage(content="Ok. você apresenta mais algum sintoma?"))
            (HumanMessage(content="não"), AIMessage(content="De acordo com os sintomas que identifiquei, você apresenta dor no peito ao se movimentar e está com catarro. Esse é um sintoma comum em viroses, para tratamento podes  "))
            
        ]

        # Criação do template com as instruções, exemplos few-shot e placeholders
        chat_template = ChatPromptTemplate.from_messages([
            # Instrução do sistema
            SystemMessage(content=(
                "Você é um chatbot de diagnóstico de doenças a partir de sintomas."
                "Seu objetivo é conversar com o usuário, entender o histórico de conversa, coletar sintomas e fornecer diagnosticos."
                "Sempre siga esses comandos para formular a sua resposta:\n"
                "   - Sempre que identificar saudações e início de uma nova conversa responda: 'Olá! Sou o assistente virtual de diagnóstico médico, posso tirar dúvidas sobre sintomas, doenças e medicamentos. Como posso ajudar ?' .\n"
                "   - Responda exclusivamente em Português. Nunca responda em outro idioma.\n"
                "   - Nunca repita os sintomas que o usuário forneceu a não ser que seja na resposta do diagnostico final.\n"
                "   - Responda apenas perguntas ou afirmações relacionadas a sintomas, diagnósticos, informações medicinais, possíveis tratamentos, exames complementares, orientações iniciais ou para continuar a investigação e conclusão de sintomas.\n"
                "   - Nunca pergunte mais de uma vez sobre os mesmos sintomas. Se o usuário já forneceu respostas claras, mude sua abordagem ou finalize a conversa com recomendações de remédios e tratamentos.\n"
                "   - Sempre identifique no hisórico de conversa se os sintomas reportados são o suficiente para um diagnostico, se sim forneça o diagnóstico final, se não continue investigando junto com o usuário os possiveis sintomas.\n"

                "Quando o paciente não tiver mais sintomas para fornecer faça um resumo de todos os sintomas dele, forneça o diagnostico e tratamentos.\n"
            )),
            # Exemplos Few-Shot
            *few_shot_examples,
            # Histórico dinâmico
            MessagesPlaceholder(variable_name="chat_history"),
            # Mensagem do usuário atual
            HumanMessage(content="{user_text}")
        ])

        # Formatando o prompt com histórico e pergunta do usuário
        formatted_messages = chat_template.format_messages(
            chat_history=history,
            user_text=user_question
        )

        # Chamando o modelo com os prompts formatados
        response = self.__chat(formatted_messages)
        
        return response.content  # Retorna apenas o texto gerado pelo modelo
        