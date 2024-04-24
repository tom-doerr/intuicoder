#!/usr/bin/env python3


import os
import uuid
import subprocess
import time

# Constant script name
SCRIPT_NAME = 'main.py'

# Constant parent directory name
GENERATED_DIR = 'generated'

# Create the 'generated' directory if it doesn't exist
os.makedirs(GENERATED_DIR, exist_ok=True)

def prepare_and_run_docker_env(python_code, parent_dir, max_execution_time=60):
    # Check if parent directory path is provided
    if not parent_dir:
        raise ValueError("Parent directory must be provided.")
    
    # Generate a unique identifier for the current run
    run_id = uuid.uuid4()
    
    # Create a new directory for the current run under the provided parent directory
    new_dir_path = os.path.join(GENERATED_DIR, parent_dir, f"run_{run_id}")
    os.makedirs(new_dir_path, exist_ok=True)

    # Set the new paths for the Python script, Dockerfile, and output files
    script_path = os.path.join(new_dir_path, SCRIPT_NAME)
    dockerfile_path = os.path.join(new_dir_path, 'Dockerfile')
    stdout_path = os.path.join(new_dir_path, 'stdout.txt')
    stderr_path = os.path.join(new_dir_path, 'stderr.txt')

    # Write the Python code to a .py file
    with open(script_path, 'w') as f:
        f.write(python_code)

    # Define Dockerfile content
    dockerfile_content = f"""
    FROM ubuntu:latest
    RUN apt-get update && apt-get install -y python3 python3-pip
    RUN pip3 install requests
    RUN pip3 install beautifulsoup4
    RUN pip3 install pipreqs
    RUN pip3 install tensorflow
    RUN pip3 install torch torchvision
    RUN pip3 install numpy
    RUN pip3 install diffusers
    WORKDIR /app
    COPY . .
    RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi
    CMD ["python3", "./{SCRIPT_NAME}"]
    """

    # Write Dockerfile
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    # Define the Docker commands to build and run the image
    build_command = f"docker build -t your-python-app-{run_id} -f {dockerfile_path} {new_dir_path}"

    # Execute the Docker build command
    os.system(build_command)

    # Define the Docker run command
    run_command = ["docker", "run", f"--name=your-python-app-container-{run_id}", f"your-python-app-{run_id}"]

    # Open files for stdout and stderr
    with open(stdout_path, 'w') as fout, open(stderr_path, 'w') as ferr:
        # Start timing the script execution
        start_time = time.time()
        # Run the command and capture stdout and stderr
        process = subprocess.Popen(run_command, stdout=fout, stderr=ferr)
        # max execution time


        process.wait()
        return_code = process.returncode
        # End timing the script execution
        end_time = time.time()

    # Calculate the total execution time
    execution_time = end_time - start_time

    # Read the stdout and stderr files
    with open(stdout_path, 'r') as f:
        stdout_text = f.read()
    with open(stderr_path, 'r') as f:
        stderr_text = f.read()

    print(f"Python script, Dockerfile created, Docker image built, and script executed. Check {new_dir_path} for the results.")

    # Return an information dictionary
    info_dict = {
        'stdout': stdout_text,
        'stderr': stderr_text,
        'execution_time': execution_time,
        'return_code': return_code,
    }
    return info_dict

# Example usage
python_code = """
print('Hallo, Ubuntu!')
"""
info_dict = prepare_and_run_docker_env(python_code, parent_dir='my_parent_directory')
print(info_dict)
