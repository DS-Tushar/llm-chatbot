import os,cfenv
import gradio as gr 
import openai

port = int(os.environ.get('PORT', 7860))
print("PORT:", port)

# Create a Cloud Foundry environment object
env = cfenv.AppEnv()

# Check if the app is running in Cloud Foundry
if env.app:
    try:
        # Get the specified user-provided service by name
        service_name = "openai_service"
        service = env.get_service(name=service_name)
        
        # Access the service credentials
        credentials = service.Credentials
        
        # Access the "openai_api_key" 
        openai_api_key = credentials['password']
        os.environ['OPENAI_API_KEY'] = openai_api_key

        openai.api_key = openai_api_key

        print("OpenAI API Key assigned")
    except Exception as err:
        print(f"The service '{service_name}' is not found.")
else:
    print("The app is not running in Cloud Foundry.")


prompt = " "

#Call the LLM Api's with a prompt/question and return a response
def generate_response(llm, prompt):
   if llm == 'OpenAI':
      completion = openai.Completion.create(
            model = "text-davinci-003",
            prompt = prompt,
            temperature = 0,
            max_tokens= 500, 
            top_p=1,
            frequency_penalty=0, 
            presence_penalty=0, 
            stop=[" Human:", " AI:"]
        ) 
      return completion.choices[0].text
   else:
      return "Unknown LLM, please choose another and retry."

#Handle the Chatbox call back
def llm_chatbot_function(llm, input, history):
    history = history or []
    my_history = list(sum(history, ()))
    my_history.append(input)
    my_input = ' '.join(my_history)
    output = generate_response(llm, my_input)
    history.append((input, output))
    return history, history 

#Define the ChatBot using Gradio Elements
def create_llm_chatbot():
    with gr.Blocks(analytics_enabled=False) as interface:
        with gr.Column():
            top = gr.Markdown("""<h1><center>LLM Chatbot</center></h1>""")
            llm = gr.Dropdown(
                    ["OpenAI", "Llama-2-7b-chat-hf"], label="LLM Choice", info="Which LLM should be used?" , value="OpenAI"
                )
        
            chatbot = gr.Chatbot()
            state = gr.State()
            question = gr.Textbox(show_label=False, placeholder="Ask me a question and press enter.") #.style(container=False)
            with gr.Row():
              summbit_btn = gr.Button("Submit")
              clear = gr.ClearButton([question, chatbot, state ])

        question.submit(llm_chatbot_function, inputs=[llm, question, state], outputs=[chatbot, state])
        summbit_btn.click(llm_chatbot_function, inputs=[llm, question, state], outputs=[chatbot, state])

    return interface

llm_chatbot = create_llm_chatbot()
    
if __name__ == '__main__': 
    llm_chatbot.launch(server_name='0.0.0.0',server_port=port)  