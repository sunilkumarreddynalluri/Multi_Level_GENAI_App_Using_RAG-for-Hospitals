from flask import Flask, render_template, request


import os

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

llm = ChatOpenAI(
    model="gpt-4o"
)

prompt = ChatPromptTemplate.from_template(
"""
You are a Hospital AI Assistant.

Answer only from the context.

<context>
{context}
</context>

Question:
{input}
"""
)

document_chain = create_stuff_documents_chain(
    llm,
    prompt
)

department_db = {

    "Reception":
        "01_reception.txt database",

    "Billing":
        "02_billing.txt database",

    "Insurance":
        "03_insurance.txt database",

    "Cardiology":
        "04_cardiology.txt database",

    "Neurology":
        "05_neurology_brain_tumor.txt database",

    "Pharmacy":
        "06_pharmacy.txt database",

    "Emergency":
        "07_emergency.txt database"
}


@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    if request.method == "POST":

        department = request.form["department"]
        question = request.form["question"]

        vector_db = Chroma(
            persist_directory=
            "./db/" + department_db[department],

            embedding_function=
            embedding_model
        )

        docs = vector_db.similarity_search(
            question,
            k=3
        )

        result = document_chain.invoke(
            {
                "input": question,
                "context": docs
            }
        )

        answer = result

    return render_template(
        "index.html",
        answer=answer
    )


if __name__ == "__main__":
    app.run(debug=True)