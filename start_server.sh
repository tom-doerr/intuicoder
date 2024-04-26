#!/bin/bash

export CUDA_VISIBLE_DEVICES=0,1
#python3 -m sglang.launch_server --model-path liuhaotian/llava-v1.6-vicuna-7b --tokenizer-path llava-hf/llava-1.5-7b-hf --chat-template vicuna_v1.1 --port 30813 --tp 2

#python3 -m sglang.launch_server --model-path MaziyarPanahi/Meta-Llama-3-70B-Instruct-GPTQ --port 38242 --tp 2
python3 -m sglang.launch_server --model-path TechxGenus/Meta-Llama-3-70B-GPTQ --port 38242 --tp 2
