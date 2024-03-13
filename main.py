import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from utils import fetch_ollama_models
import tempfile
import os
import requests

DB_FAISS_PATH = 'vectorstore/db_faiss'

st.set_page_config(page_title="Chat with Document")
st.title("Chat with Document")

ollama_url = st.sidebar.text_input("Ollama Deployment's URL", os.environ.get("OLLAMA_URL"))

if ollama_url:
    try:
        ollama_models = fetch_ollama_models(ollama_url)
        selected_model = st.sidebar.selectbox("Select the LLM Model", ollama_models)
        
        uploaded_doc = st.sidebar.file_uploader(
            "Upload the document you want to chat about",
            type="pdf"
        )
        
        if uploaded_doc:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_doc.getvalue())
                tmp_file_path = tmp_file.name
        
            pdf_loader = PyPDFLoader(tmp_file_path)
            pages = pdf_loader.load()
            
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})
        
            db = FAISS.from_documents(pages, embeddings)
            db.save_local(DB_FAISS_PATH)
        
            llm = Ollama(model=selected_model, base_url=ollama_url)
            chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())
        
            def conversational_chat(query):
                result = chain({"question": query, "chat_history": st.session_state['history']})
                st.session_state['history'].append((query, result["answer"]))
                return result["answer"]
        
            if 'history' not in st.session_state:
                st.session_state['history'] = []
        
            if 'generated' not in st.session_state:
                st.session_state['generated'] = ["Hello! You can ask me anything about the document: " + uploaded_doc.name]
        
            if 'past' not in st.session_state:
                st.session_state['past'] = ["Hey! I've uploaded a document"]
        
            response_container = st.container()
            container = st.container()
        
            with container:
                user_input = st.chat_input(placeholder="Discuss about the uploaded document", key='input')
        
                if user_input:
                    st.session_state['past'].append(user_input)
                    output = conversational_chat(user_input)
                    st.session_state['generated'].append(output)
        
            if st.session_state['generated']:
                with response_container:
                    for i in range(len(st.session_state['generated'])):
                        with st.chat_message("user"):
                            st.write(st.session_state["past"][i])
                        with st.chat_message("assistant"):
                            st.write(st.session_state["generated"][i])
    except requests.exceptions.ConnectionError as e:
        st.text("No Ollama deployment found at {}".format(os.environ.get("OLLAMA_URL"))) 
    
