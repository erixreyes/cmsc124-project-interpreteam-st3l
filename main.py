import subprocess
import os

def run_script(script_name):
    """Run a Python script and check for errors."""
    result = subprocess.run(
        ["python", script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        return False
    print(result.stdout)
    return True

def main():
    # Step 1: Run lexical.py
    print("Running lexical.py...")
    if not run_script("lexical.py"):
        print("lexical.py failed. Exiting.")
        return
    
    # Check if output.txt is generated
    if not os.path.exists("output.txt"):
        print("Error: output.txt not found after running lexical.py.")
        return

    # Step 2: Run new_parse.py
    print("Running new_parse.py...")
    if not run_script("new_parse.py"):
        print("new_parse.py failed. Exiting.")
        return

    print("Both scripts ran successfully.")

if __name__ == "__main__":
    main()
