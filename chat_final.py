import openai
import json
import fitz  # PyMuPDF
import os
from openai import OpenAI
from IPython.display import Image, display
import time
import pandas as pd

OPENAI_KEY="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" 



#helper function that formats and prints the Assistants API object
def show_json(obj):
    display(json.loads(obj.model_dump_json()))



client = OpenAI(api_key=OPENAI_KEY)

#create an assistant, with code interpreter and retrieval tools 
assistant = client.beta.assistants.create(
    name = "Finance Insight Analyst",
    instructions = "You are a helpful financial analyst expert and your are tailored for in-depth SEC 10-Q filings analysis, focusing on management discussions and financial results.",
    tools = [{"type":"code_interpreter"}, {"type": "retrieval"}],
    model = "gpt-4-1106-preview"
)

#show_json(assistant)

#asst_ocospvga0bLal7o0zsy3nt8h

#thread holds a conversation session between an Assistant and a user
thread1 = client.beta.threads.create()


#as the user asks questions, we add the messages to the thread
#then run the assistant on the thread - assistant calls relevant tools

#creating a Run: returns with Run's metadata, including status that starts as queued
#status updates -> we can check Run's status in a loop


#submits a new user message to a thread and runs the Assistant on the thread 
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


#track when the Assistant has finished processing so we can retrieve a response from the Assistant
# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run



#once run is completed, we use this function to retrieve the response from the thread
def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


# Pretty printing helper
#def pretty_print(messages):
#    print("# Messages")
#    for m in messages:
#        print(f"{m.role}: {m.content[0].text.value}")
#    print()


def pretty_print(messages):
    print("# Messages")
    for m in messages:
        if m.content[0].type == "text":
            print(f"{m.role}: {m.content[0].text.value}")
        elif m.content[0].type == "image_file":
            print(f"{m.role}: Image file received")
            # You can optionally include code here to save or display the image
        else:
            print(f"{m.role}: Unknown content type")

    print()




def upload_and_update_assistant(client, assistant_id, file_paths):
    # Upload the files
    file_ids = []
    for file_path in file_paths:
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants",
        )
        file_ids.append(file.id)

    # Update Assistant with the new files
    assistant = client.beta.assistants.update(
        assistant_id,
        file_ids=file_ids,
    )

    show_json(assistant)
    return file_ids




#test 1 file - making a graph:
# Upload the file
file = client.files.create(
    file=open(
        "cisco1.pdf",
        "rb",
    ),
    purpose="assistants",
)


# Update Assistant
assistant = client.beta.assistants.update(
    assistant.id,
    file_ids=[file.id],
)
#show_json(assistant)

uploaded_files = client.files.list()
file_objects = list(filter(lambda x: x.filename == "cisco1.pdf", uploaded_files.data))

if len(file_objects) > 0:
  file_id = file_objects[0].id

thread = client.beta.threads.create()
#run = submit_message(assistant.id, thread, "What are the current and total assets in this 10Q filing?")
#run = wait_on_run(run, thread)
#pretty_print(get_response(thread))



#run = submit_message(assistant.id, thread, "What are the current and total assets in this 10Q filing?")
#run = wait_on_run(run, thread)
#messages = get_response(thread)


#run = submit_message(assistant.id, thread, "Can you extract the financial summary data and put it in CSV")
#run = wait_on_run(run, thread)
#messages = get_response(thread)
#pretty_print(messages)

#file_path = messages.data[-1].content[0].text.annotations[0].file_path.file_id

#file_name = client.files.with_raw_response.retrieve_content(file_path)
#output_file_name = "data.csv"
#with open(output_file_name, "wb") as file:
#    file.write(file_name.content)


#df = pd.read_csv("data.csv")
#print(df.head(12))




#thread3 = client.beta.threads.create()
#run3 = submit_message(assistant.id, thread3, "can you draw a line graph based on operational margins in the file? Even if it's 2 points that's fine.")
#run3 = wait_on_run(run3, thread3)
#messages = get_response(thread3)

#pretty_print(messages)

#file_path = messages.data[-1].content[0].image_file.file_id

#file_name = client.files.with_raw_response.retrieve_content(file_path)
#output_file_name = "margin.png"
#with open(output_file_name, "wb") as file:
#    file.write(file_name.content)

#image_path = output_file_name
#display(Image(filename=image_path))




# Function definition
def send_email(email, textbody, subject="Financial Statement Summary"):
    print("Email sent")

# Dictionary for function metadata
function_send_email_metadata = {
    "name": "send_email",
    "description": "A function that takes in a user email, a subject line and body text and sends an email to the email address provided",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "the email address of the user who receives the email"},
            "subject": {"type": "string", "description": "subject line of the email"},
            "textbody": {"type": "string", "description": "the body of the email."}
        }
    },
    "required": ["email", "subject", "textbody"]
}

# Update assistant with function metadata
assistant = client.beta.assistants.update(
    assistant.id,
    tools=[
        {"type": "code_interpreter"},
        {"type": "retrieval"},
        {"type": "function", "function": function_send_email_metadata},
    ],
)

# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    if run.status == "requires_action":
        tools_to_call = run.required_action.submit_tool_outputs.tool_calls
        print(len(tools_to_call))
        print(tools_to_call)

        tool_output_array = []

        for each_tool in tools_to_call:
            tool_id = each_tool.id
            function_name = each_tool.function.name
            function_arg = each_tool.function.arguments

            if function_name == "send_email":
                arguments = json.loads(function_arg)
                send_email(arguments["email"], arguments["subject"], arguments["textbody"])
                print(arguments["email"])
                print(arguments["subject"])
                print(arguments["textbody"])
                output = "Mail sent OK"
                tool_output_array.append({"tool_call_id": tool_id, "output": output})

        # Return results to the run operation
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_output_array
        )

    return run

# ... (rest of the code)



thread =  client.beta.threads.create()
run = submit_message(assistant.id, thread, "Can you send the summary to the mail: nishkachotai@gmail.com?")
run = wait_on_run(run, thread)

show_json(run)

pretty_print(get_response(thread))



