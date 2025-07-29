import subprocess
import sys

def check_npx():
    try:
        # Try to run npx --version to check if it's installed
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True, check=True)
        print(f"npx is installed. Version: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("npx command failed.")
        return False
    except FileNotFoundError:
        print("npx is not found. Please install Node.js which includes npx.")
        return False

if __name__ == "__main__":
    check_npx()