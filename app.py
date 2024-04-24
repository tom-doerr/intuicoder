#!/usr/bin/env python3


import gradio as gr
import openai
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import transformers
import torch
import os
from execute_code import prepare_and_run_docker_env
import pandas as pd

# Setzen Sie Ihren OpenAI-API-Schlüssel hier
openai.api_key = 'YOUR_OPENAI_API_KEY'

INSTRUCTION_FILE = 'instruction.md'

# Lade gespeicherte Anweisungen
if os.path.exists(INSTRUCTION_FILE):
    with open(INSTRUCTION_FILE, 'r') as f:
        saved_instruction = f.read()
else:
    saved_instruction = ''

# @st.cache_resource
def load_lm(model_name):
    device_map = 0
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.bfloat16, device_map=device_map)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer, model

def extract_code_from_text(text):
    print("text:", text)
    text = text.split('```python')
    text = text[1].split('```')
    text = text[0]
    return text

def generate_code(instruction, model_name, num_runs, temperature, max_tokens):
    tokenizer, model = load_lm(model_name)
    prompt = f'''
    {instruction}
    Just respond with the code, no explanation needed.

    ```python
    #!/usr/bin/env python3
    '''
    inputs = tokenizer([prompt], return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    if 'token_type_ids' in inputs:
        del inputs["token_type_ids"]

    codes, stdouts, stderrs = [], [], []
    for _ in range(num_runs):
        streamer = TextIteratorStreamer(tokenizer)
        generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
        tokens = model.generate(**generation_kwargs)

        text_all = tokenizer.decode(tokens[0], skip_special_tokens=True)

        code = extract_code_from_text(text_all)
        info = prepare_and_run_docker_env(code, 'run_1')

        codes.append(code)
        stdouts.append(info['stdout'])
        stderrs.append(info['stderr'])

    return codes[0], stdouts, stderrs

# Eingabekomponenten
inputs = [
    gr.inputs.Textbox(label="Instruction", default=saved_instruction),
    gr.inputs.Dropdown(choices=[
        'WizardLM/WizardCoder-15B-V1.0',
        'EleutherAI/gpt-neo-2.7B',
        'lmsys/vicuna-7b-v1.3',
        'lmsys/vicuna-33b-v1.3',
        'tiiuae/falcon-7b-instruct',
        'tiiuae/falcon-40b-instruct',
        'THUDM/chatglm2-6b',
        'mosaicml/mpt-7b-chat',
        'mosaicml/mpt-30b-chat'
        'replit/replit-code-v1-3b',
        'meta-llama/Llama-2-7b-chat-hf',
    ], label="Model", default='tiiuae/falcon-7b-instruct'),
    gr.inputs.Slider(minimum=1, maximum=100, default=1, label="Number of runs"),
    gr.inputs.Slider(minimum=0.0, maximum=2.0, step=0.1, default=1.0, label="Temperature"),
    gr.inputs.Slider(minimum=1, maximum=5000, default=100, label="Max tokens")
]

# Ausgabekomponenten
outputs = [
    gr.outputs.Textbox(label="Generated Code"),
    gr.outputs.Textbox(label="Standard Output"),
    gr.outputs.Textbox(label="Error Output")
]

# Erstellen Sie die Schnittstelle
interface = gr.Interface(fn=generate_code, inputs=inputs, outputs=outputs)

# Starten Sie die App
interface.launch()
