#!/usr/bin/env python3


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import os

app = FastAPI()

# Setzen Sie Ihren OpenAI-API-Schlüssel hier
openai.api_key = 'YOUR_OPENAI_API_KEY'

def load_lm(model_name):
    device_map = 0
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.bfloat16, device_map=device_map)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer, model

def extract_code_from_text(text):
    text = text.split('```python')
    text = text[1].split('```')
    text = text[0]
    return text


class GeneratePayload(BaseModel):
    instruction: str = "Write a hello world program in Python."
    model_name: str = "tiiuae/falcon-7b-instruct"
    num_runs: int = 1
    temperature: float = 1.0
    max_tokens: int = 100


def generate_code(instruction, model_name, num_runs, temperature, max_tokens):
# def generate_code(payload: GeneratePayload):

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
        # Hier fehlt die 'prepare_and_run_docker_env' Methode von Ihrem vorherigen Beispiel,
        # also habe ich diesen Teil für den Moment auskommentiert
        # info = prepare_and_run_docker_env(code, 'run_1')

        codes.append(code)
        # stdouts.append(info['stdout'])
        # stderrs.append(info['stderr'])

    return codes[0], stdouts, stderrs

class GenerationInput(BaseModel):
    # instruction: str
    # model_name: str
    # num_runs: int
    # temperature: float
    # max_tokens: int
    instruction: str = "Write a hello world program in Python."
    model_name: str = "tiiuae/falcon-7b-instruct"
    num_runs: int = 1
    temperature: float = 1.0
    max_tokens: int = 100


@app.post("/generate/")
async def generate_text(data: GenerationInput):
    try:
        instruction = data.instruction
        model_name = data.model_name
        num_runs = data.num_runs
        temperature = data.temperature
        max_tokens = data.max_tokens

        generated_code, std_out, err_out = generate_code(instruction, model_name, num_runs, temperature, max_tokens)

        return {
            "generated_code": generated_code,
            "standard_output": std_out,
            "error_output": err_out
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
