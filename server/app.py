from flask import Flask, request, jsonify
import os
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.replicate import Replicate
from transformers import AutoTokenizer
try:
    from flask_cors import CORS
    print("Flask-CORS is installed and importable.")
except ImportError as e:
    print(f"ImportError: {e}")

from dotenv import load_dotenv
load_dotenv()

os.environ["REPLICATE_API_TOKEN"] = os.getenv('API_KEY')

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    documents = SimpleDirectoryReader("uploads/").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
    )
    query_engine = index.as_query_engine()

    response =  query_engine.query(f"{query}")
    return response.to_dict() if hasattr(response, 'to_dict') else str(response)


@app.route('/api/execute', methods=['POST'])
def execute_function():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        query = request.form.get('query')
        answer = simple_python_function(query)
        return jsonify({ 'answer': answer })

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
