from flask import Flask, request, jsonify
import os
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.replicate import Replicate
from transformers import AutoTokenizer

from dotenv import load_dotenv
load_dotenv()

os.environ["REPLICATE_API_TOKEN"] = os.getenv('API_KEY')

app = Flask(__name__)

def simple_python_function(query):
    llama2_7b_chat = "meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e"
    Settings.llm = Replicate(
        model=llama2_7b_chat,
        temperature=0.01,
        additional_kwargs={"top_p": 1, "max_new_tokens": 300},
    )

    Settings.tokenizer = AutoTokenizer.from_pretrained(
        "NousResearch/Llama-2-7b-chat-hf"
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    documents = SimpleDirectoryReader("./").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
    )
    query_engine = index.as_query_engine()

    response =  query_engine.query(f"{query}")
    return response.to_dict() if hasattr(response, 'to_dict') else str(response).replace('\n',' ').replace('\\n',' ')

@app.route('/api/execute', methods=['POST'])
def execute_function():
    if request.method == 'POST':
        query = request.json.get("query")
        answer = simple_python_function(query)
        return jsonify({ 'answer': answer })

if __name__ == '__main__':
    app.run(debug=True)
