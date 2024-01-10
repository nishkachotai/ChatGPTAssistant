import openai
import json
import fitz  # PyMuPDF
import os
from openai import OpenAI
from IPython.display import display


# Set your OpenAI API key
# openai.api_key = "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"



def show_json(obj):
    display(json.loads(obj.model_dump_json()))


###########

def extract_text_from_pdf(pdf_path):
    try:
        print(f"Attempting to extract text from: {pdf_path}")
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        print(f"Successfully extracted text from: {pdf_path}")
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""





############

def split_text(text):
    max_chunk_size = 1000
    chunks = []
    current_chunk = ""
    for sentence in text.split("."):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


#############


client = OpenAI(api_key="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")

assistant = client.beta.assistants.create(
    name = "News Summarizer",
    instructions = "You are a helpful news summarizer that will summarize news articles.",
    tools = [{"type":"code_interpreter"}, {"type": "retrieval"}],
    model = "gpt-4-1106-preview"
)

show_json(assistant)


###############

thread1 = client.beta.threads.create()


def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


import time
# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


##################


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


##################



# List of PDF filenames to process
pdf_filenames = ["Q1cisco.pdf", "Q2cisco.pdf", "Q3cisco.pdf", "Q4cisco.pdf"]

# List to store text from each PDF
pdf_texts = []

# Iterate through specified PDF filenames
for filename in pdf_filenames:
    pdf_path = os.path.join(os.path.expanduser("~/Desktop"), filename)
    pdf_text = extract_text_from_pdf(pdf_path)
    #print(pdf_text)
    pdf_texts.append(pdf_text)

# Concatenate text from all PDFs into a single string
combined_text = "\n".join(pdf_texts)

# Ask a question relevant to all PDFs
run1 = submit_message('asst_nakVX0SJYZwo8i1LSh6mEQV2', thread1, f"Please provide the total assets of these 4 quarterly results for Cisco Systems, you just need to add up the 4 total assets and print out that number.\n{combined_text}")
run1 = wait_on_run(run1, thread1)
pretty_print(get_response(thread1))




