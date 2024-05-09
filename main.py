#!/usr/bin/env python3

import os
from sglang import function, system, user, assistant, gen, set_default_backend, RuntimeEndpoint
import run_config

set_default_backend(RuntimeEndpoint("http://localhost:38242"))
print('Backend set')


@function
def multi_turn_question(s, question_1, question_2):
    s += system("You are a helpful assistant.")
    s += user(question_1)
    s += assistant(gen("answer_1", max_tokens=256))
    s += user(question_2)
    s += assistant(gen("answer_2", max_tokens=256))


def test_sglang():
    state = multi_turn_question.run(
        question_1="What is the capital of the United States?",
        question_2="List two local attractions.",
    )

    for m in state.messages():
        print(m["role"], ":", m["content"])

    print(state["answer_1"])


PREFIX_PATTERN = '#- '
FILES_TO_IGNORE = ['__init__.py', '__pycache__', '.git', '.gitignore']
EXCLUDE_DOT_FILES = True


@function
def generate_code(s, code_before_with_line_numbers, code_after_with_line_numbers, instruction):
    s += "It's your task to write code following the following instruction:\n"
    s += "Instruction: " + instruction + "\n"
    s += "Code after the instruction:\n"
    s += "```python\n"
    s += code_after_with_line_numbers + "\n\n"
    s += "```"
    s += "Code before the instruction:\n"
    s += "```python\n"
    s += code_before_with_line_numbers + "\n\n"
    s += "```"
    s += "Please write the code below.\n"
    s += "Code in between the two code blocks:\n"
    s += "```python\n"
    s += gen("code_with_line_numbers", max_tokens=1024, stop=["```", "\nassert"])
    s += "```\n\n"
    s += "Same code in between the two code blocks but without line numbers:\n"
    s += "```python\n"
    s += gen("code", max_tokens=1024, stop=["```", "\nassert"])


def get_matching_line(file_content, prefix_pattern):
    lines = file_content.split('\n')
    # matching_lines = []
    for i, line in enumerate(lines):
        if prefix_pattern in line:
            # matching_lines.append(i)
            return i, line

    assert False, "No matching line found"

def get_first_assert_line_after(instruction_line_number, file_content):
    lines = file_content.split('\n')
    for i in range(instruction_line_number, len(lines)):
        if 'assert' in lines[i]:
            return i, lines[i]
    assert False, "No assert line found"

# search all files recursively in the directory for prefix pattern
def search_files(root_dir='.'):
    files = []
    # matching_files = []
    for root, dirs, files in os.walk(root_dir):
        print("dirs:", dirs)
        if EXCLUDE_DOT_FILES:
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']
        # exclude ..
        if root == '.':
            dirs[:] = [d for d in dirs if not d == '..']
        print("files:", files)
        # input()
        for file in files:
            print("file:", file)
            if file not in FILES_TO_IGNORE:
                with open(os.path.join(root, file), 'r') as f:
                    try:
                        f_content = f.read()
                    except UnicodeDecodeError:
                        pass

                    if PREFIX_PATTERN in f_content:
                        # matching_files.append(file)
                        return file

    # return matching_files

def get_surrounding_lines(file_content, instruction_line_number, assert_line_number):
    lines = file_content.split('\n')
    code_before = ''
    code_after = ''
    for i, line in enumerate(lines):
        if i < instruction_line_number:
            code_before += line + '\n'
        # elif i > assert_line_number:
        elif i > assert_line_number - 1:
            code_after += line + '\n'

    return code_before, code_after

def extract_instruction(instruction_line):
    return instruction_line.split(PREFIX_PATTERN)[1]

def add_line_numbers(text, start_line_number):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        lines[i] = f"{start_line_number + i} {line}"
    return '\n'.join(lines)

def insert_code(file_path, code, line_number):
    with open(file_path, 'r') as f:
        f_content = f.read()

    lines = f_content.split('\n')
    lines.insert(line_number, code)
    new_content = '\n'.join(lines)

    with open(file_path, 'w') as f:
        f.write(new_content)

import subprocess
def run_program():
    run_command = run_config.config['run_command']
    print("run_command:", run_command)
    process = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print("Output:")
    print(process.stdout.read())
    exit_code = process.returncode
    return exit_code == 0

def main():
    attempt = 0
    while True:
        file_path = search_files()
        with open(file_path, 'r') as f:
            f_content = f.read()
        instruction_line_number, instruction_line = get_matching_line(f_content, PREFIX_PATTERN)
        print("instruction_line_number:", instruction_line_number)
        print("instruction_line:", instruction_line)
        assert_line_number, assert_line = get_first_assert_line_after(instruction_line_number, f_content)
        print("assert_line_number:", assert_line_number)
        print("assert_line:", assert_line)
        code_before, code_after = get_surrounding_lines(f_content, instruction_line_number, assert_line_number)
        print("code_before:", code_before)
        print("code_after:", code_after)
        instruction = extract_instruction(instruction_line)
        code_before_with_line_numbers = add_line_numbers(code_before, 1)
        code_after_with_line_numbers = add_line_numbers(code_after, assert_line_number + 1)
        state = generate_code.run(
            code_before_with_line_numbers=code_before_with_line_numbers,
            code_after_with_line_numbers=code_after_with_line_numbers,
            instruction=instruction,
            temperature=0.5
        )
        print("state:", state)
        code = state["code"]
        print("code:", code)
        with open(file_path, 'r') as f:
            original_file_content = f.read()

        insert_code(file_path, code, instruction_line_number + 1)
        success = run_program()
        print("success:", success)
        attempt += 1
        if not success:
            with open(file_path, 'w') as f:
                f.write(original_file_content)
            print("Code reverted to original")
        else:
            print(f"Code successfully inserted after {attempt} attempts")
            break




if __name__ == "__main__":
    # test_sglang()
    # print(search_files())
    main()











