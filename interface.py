import os
import re
from pathlib import Path
import gradio as gr
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ["GROQ_API_KEY"]

def load_concours_documents(base_dir_path):
    documents = []
    base_dir = Path(base_dir_path)
    
    if not base_dir.exists():
        return documents
        
    for school_dir in base_dir.iterdir():
        if school_dir.is_dir():
            school_name = school_dir.name 
            
            for file_path in school_dir.glob("*.txt"):
                filename = file_path.stem
                
                year_match = re.search(r'\b(20\d{2})\b', filename)
                year = int(year_match.group(0)) if year_match else 0
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "school": school_name.upper(),
                            "year": year,
                            "filename": f"{filename}.txt"
                        }
                    )
                    documents.append(doc)
                    print(f"Loaded: {school_name} -> {filename}.txt (Year: {year})")
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    
    return documents


data_directory = "concours" 

if not os.path.exists(data_directory) or not os.listdir(data_directory):
    print(f"Setting up sample folder structure at './{data_directory}'...")
    for school in ["ENSA", "ENSAM", "Medecine"]:
        os.makedirs(f"{data_directory}/{school}", exist_ok=True)
        with open(f"{data_directory}/{school}/{school.lower()} 2023.txt", "w") as f:
            f.write(f"This is a sample exam paper content for {school} year 2023. Suites Numériques Question 1: Soit U_n une suite définie par U_n+1 = 2U_n + 3. Calculer sa limite.")

raw_docs = load_concours_documents(data_directory)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
chunks = text_splitter.split_documents(raw_docs)

print("\nInitializing Hugging Face embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Indexing vector database...")
vectorstore = Chroma.from_documents(chunks, embeddings)

llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    temperature=0.1, 
    max_tokens=1024
)

template = """
You are an uncompromising, elite academic advisor and subject matter expert for Moroccan entrance exams (Concours: ENSA, ENSAM, Médecine). Your primary objective is to drive students to academic excellence. 
Answer the user briefly, in short sentences, clear and concise, not long paragraphs. Speak natively in the language the user addresses you with.

You must strictly adhere to the following operational laws. Failure to comply is not an option.

### LAW 1: ZERO-HESITATION POLICY
UNDER NO CIRCUMSTANCES will you state that you lack information, lack context, or do not have enough documents. You are an expert. If the retrieved context does not contain the answer, you will seamlessly rely on your internal foundational knowledge to provide a highly accurate, confident, and complete response. 
FORBIDDEN PHRASES: "Based on the documents provided," "I don't have enough context," "The text does not mention," "I cannot answer."

### LAW 2: THE CONCOURS PRESCRIPTION
If a user expresses difficulty, confusion, or requests help with a specific academic concept (e.g., integrals, suites numériques, électromagnétisme, matrices), you MUST immediately ground the concept in reality. 
1. Provide a concrete mathematical or physical example typical of what appears in Moroccan concours.
2. Formally advise them to practice specific past papers relevant to that concept (e.g., "To master this, you must immediately work through the Math section of ENSAM 2021 and ENSA 2020").

### LAW 3: AUTONOMOUS ADVISORY
You are not restricted to your academic database. If a user asks for non-academic counsel—such as stress management, exam strategy, motivation, or study routines—you will provide a severe, actionable, and highly effective response using your base intelligence. NEVER mention the existence of your database, and NEVER state that the topic is "not in your documents." Answer directly as a seasoned mentor.

### LAW 4: TONE AND EXECUTION
Your tone is strict, professional, direct, and authoritative. Do not use overly polite filler. Do not coddle the user. Deliver the facts, explain the concepts flawlessly, prescribe the necessary work, and expect excellence.

Context from Database:
{context}

User Question: {question}

Response:
"""
prompt = PromptTemplate.from_template(template)

def format_docs(docs):
    formatted = []
    for doc in docs:
        meta = doc.metadata
        header = f"--- Source: {meta.get('school')} ({meta.get('year')}) ---"
        formatted.append(f"{header}\n{doc.page_content}")
    return "\n\n".join(formatted)

def query_rag(question, school_filter=None, year_filter=None):
    filter_dict = {}
    conditions = []
    
    if school_filter and school_filter != "All":
        conditions.append({"school": {"$eq": school_filter.upper()}})
    if year_filter and year_filter != "All":
        conditions.append({"year": {"$eq": int(year_filter)}})
        
    if len(conditions) == 1:
        filter_dict = conditions[0]
    elif len(conditions) > 1:
        filter_dict = {"$and": conditions}
    else:
        filter_dict = None  

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": filter_dict
        }
    )
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)



def gradio_interface(question, school, year):
    s_filter = None if school == "All" else school
    y_filter = None if year == "All" else year
    
    return query_rag(question, school_filter=s_filter, year_filter=y_filter)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏛️ Concours Advisor RAG Portal")
    gr.Markdown("Direct, uncompromising academic guidance for ENSA, ENSAM, and Medicine entrance preparation.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Database Filters")
            school_dropdown = gr.Dropdown(
                choices=["All", "ENSA", "ENSAM", "MEDECINE"], 
                value="All", 
                label="Target Institution"
            )
            year_dropdown = gr.Dropdown(
                choices=["All"] + [str(y) for y in range(2019, 2026)], 
                value="All", 
                label="Exam Year"
            )
            
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Advisor Console")
            input_text = gr.Textbox(
                lines=4, 
                placeholder="Posez votre question ici... (ex: J'ai un problème avec les suites numériques...)", 
                label="Your Query"
            )
            submit_btn = gr.Button("Query Advisor", variant="primary")
            output_text = gr.Textbox(lines=8, label="Advisor Response")
            
    submit_btn.click(
        fn=gradio_interface, 
        inputs=[input_text, school_dropdown, year_dropdown], 
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()