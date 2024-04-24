#!/usr/bin/env python3


import gradio as gr
import time

def update_unix_time():
    while True:
        time.sleep(1)
        current_time = str(int(time.time()))
        gr.update(value=current_time)

# Startet den Update-Thread
gr.Interface(
    update_unix_time, 
    inputs=None,
    outputs=gr.Textbox(label="Current Unix Time")
).launch(inbrowser=True)
