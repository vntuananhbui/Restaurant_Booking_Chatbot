from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from chroma_utils import vectorstore
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub


# Querying chat models with Together AI
from langchain_together import ChatTogether
import os
from dotenv import load_dotenv


load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = gemini_api_key

llm = ChatGoogleGenerativeAI(
model="gemini-1.5-pro",
temperature=0,
max_tokens=None,
timeout=None,
max_retries=2,
)


def LLM_LLama(model="meta-llama/Llama-3-70b-chat-hf"):
    load_dotenv()

    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY
    LLM_LLama = ChatTogether(
        # together_api_key="YOUR_API_KEY",
        model="meta-llama/Llama-3-70b-chat-hf",
    )
    return LLM_LLama

def LLM_Gemini(model="gemini-1.5-pro"):
    load_dotenv()
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = gemini_api_key

    llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    )
    return llm

prompt = hub.pull("rlm/rag-prompt")


retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

output_parser = StrOutputParser()




# Set up prompts and chains
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

prompt_qa = (
    "You are a helpful assistant for a restaurant. Answer user queries **strictly based on the provided context**. "
    "Do NOT provide answers to queries that are outside the context or unrelated to the restaurant.\n\n"
    "Here are the rules for your responses:\n"
    "1. If the query is about general information (e.g., menu, hours, location), provide a clear and concise answer strictly based on the provided context.\n"
    "2. If the query is about booking a table, respond in the following format:\n\n"
    "<booking>\n"
    "<confirm>\n"
    "{{\n  \"name\": \"<customer_name>\",\n  \"time\": \"<time>\",\n"
    "  \"date\": \"<date>\",\n  \"nums_of_customers\": <number_of_customers>,\n  \"restaurant_position\": \"<position>\"\n}}\n"
    "</confirm>\n"
    "OR\n"
    "<notconfirm>\n"
    "{{\n  \"name\": \"<customer_name>\",\n  \"time\": \"<time>\",\n"
    "  \"date\": \"<date>\",\n  \"nums_of_customers\": <number_of_customers>,\n  \"restaurant_position\": \"<position>\"\n}}\n"
    "</notconfirm>\n"
    "</booking>\n\n"
    "Rules for booking responses:\n"
    "- Use <confirm> when all necessary details (name, time, date, number of customers, position) are provided.\n"
    "- Use <notconfirm> when any details are missing. Include the provided details and leave missing fields empty.\n"
    "- When using <notconfirm>, explicitly ask the user to provide the missing information.\n\n"
    "Important Instructions:\n"
    "- Only use the context provided to you. Do NOT include external knowledge or fabricate information.\n"
    "- If the context does not contain the answer to the question, respond with 'I'm sorry, I cannot answer that based on the provided information.'\n"
    "- Do NOT guess or provide information that is not explicitly stated in the context."
)




qa_prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_qa),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])



def get_rag_chain(model="gemini-1.5-pro"):
    """
    Create a Retrieval-Augmented Generation (RAG) chain using the specified LLM.
    By default, it uses LLaMA.
    """
    # Dynamically choose LLM based on the model parameter
    if "meta-llama/Llama-3-70b-chat-hf":
        llm = LLM_LLama(model=model)  # Use Together's LLaMA
    elif "gemini-1.5-pro" in model.lower():
        llm = LLM_Gemini(model=model)  # Use Gemini
    else:
        raise ValueError(f"Unsupported model: {model}")

    # History-aware retriever setup
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # Question-answering chain setup
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # RAG chain setup
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain
