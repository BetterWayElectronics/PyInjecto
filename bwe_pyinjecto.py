import sys
import os
import glob
import time
import subprocess
import psutil
import ctypes
import ast
import math

# ---- Color Definitions (ANSI Escape Codes) ----
THEME_LIGHT_RED = "\033[38;2;255;128;128m"  # For errors or warnings
THEME_DARK_PURPLE   = "\033[38;2;85;0;145m"    # For errors
THEME_INTERMEDIATE1 = "\033[38;2;99;43;153m"   # For option labels
THEME_INTERMEDIATE2 = "\033[38;2;122;87;176m"  # For prompts
THEME_INTERMEDIATE3 = "\033[38;2;146;130;199m" # For informational messages
THEME_LIGHT_BLUE    = "\033[38;2;173;216;230m" # For successes
RESET               = "\033[0m"

# ============================
# Banner Function
# ============================
def print_banner() -> str:
    # Optionally, resize the terminal if supported.
    sys.stdout.write("\x1b[8;32;130t")
    banner = f"""{THEME_LIGHT_BLUE}
__________        .___            __               __          
\\______   \\___.__.|   | ____     |__| ____   _____/  |_  ____  
 |     ___<   |  ||   |/    \\    |  |/ __ \\_/ ___\\   __\\/  _ \\ 
 |    |    \\___  ||   |   |  \\   |  \\  ___/\\  \\___|  | (  <_> )
 |____|    / ____||___|___|  /\\__|  |\\___  >\\___  >__|  \\____/ By BwE 2025
           \\/              \\/\\______|    \\/     \\/    
  Inject Code Into Python Apps Via PyInjector or Hypno Terminal{RESET}
"""
    return banner

print(print_banner())

# ============================
# Process Selection Functions
# ============================
def list_running_processes():
    """Return A List Of Dicts With Process 'Pid' And 'Name'."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processes.append(proc.info)
        except psutil.NoSuchProcess:
            continue
    return processes

def print_process_list(processes):
    #Prints the list of running processes.
    print(f"{THEME_INTERMEDIATE3}Currently Running Processes:{RESET}")
    for proc in processes:
        print(f"{THEME_INTERMEDIATE1}PID:{RESET} {proc['pid']:<6} {THEME_INTERMEDIATE1}- Name:{RESET} {proc.get('name','')}")

def search_processes(keyword, processes):
    #Searches for processes matching the given keyword.
    keyword = keyword.lower()
    return [proc for proc in processes if proc.get('name') and keyword in proc['name'].lower()]

def choose_process():
    #Prompts the user to choose a process by entering a keyword or using !list.
    processes = list_running_processes()

    while True:
        selection = input(f"\n{THEME_INTERMEDIATE2}Enter A Keyword To Search For A Process, Or Type '!list' To View All: {RESET}").strip()

        if selection.lower() == "!list":
            os.system('cls' if os.name == 'nt' else 'clear')  # Clears the screen
            print_banner()
            print_process_list(processes)
            continue  # Re-prompt user

        if selection.isdigit():
            pid = int(selection)
            try:
                psutil.Process(pid)  # Verify Process Exists
                return pid
            except psutil.NoSuchProcess:
                print(f"{THEME_LIGHT_RED}No Process With That PID Found.{RESET}")
                continue  # Re-prompt user
        else:
            matches = search_processes(selection, processes)
            if not matches:
                print(f"{THEME_LIGHT_RED}No Processes Found Matching That Keyword.{RESET}")
                continue  # Re-prompt user
            elif len(matches) == 1:
                proc = matches[0]
                print(f"{THEME_LIGHT_BLUE}Found One Match: PID: {proc['pid']} - Name: {proc['name']}{RESET}")
                return proc['pid']
            else:
                print(f"\n{THEME_INTERMEDIATE3}Multiple Matches Found:{RESET}")
                for i, proc in enumerate(matches):
                    print(f"{THEME_INTERMEDIATE1}{i+1}:{RESET} PID: {proc['pid']} - Name: {proc['name']}")
                while True:
                    choice = input(f"\n{THEME_INTERMEDIATE2}Select A Process By Number: {RESET}").strip()
                    if choice.isdigit():
                        index = int(choice) - 1
                        if 0 <= index < len(matches):
                            return matches[index]['pid']
                    print(f"\n{THEME_LIGHT_RED}Invalid Selection, Try Again.{RESET}")

# =======================
# DLL & Hypno Injection Functions
# =======================
def list_dlls(prefix="pyinjector"):
    #Return A List Of DLL Files In The Current Directory That Start With Prefix (Case-Insensitive).
    return [dll for dll in glob.glob("*.dll") if dll.lower().startswith(prefix.lower())]

def choose_dll():
    dlls = list_dlls()
    if not dlls:
        print(f"{THEME_LIGHT_RED}No DLL Files Found Starting With 'Pyinjector' In The Current Directory.{RESET}")
        sys.exit(1)
    print(f"\n{THEME_INTERMEDIATE3}Available DLL Files:{RESET}")
    for i, dll in enumerate(dlls):
        print(f"{THEME_INTERMEDIATE1}{i+1}:{RESET} {dll}")
    while True:
        choice = input(f"\n{THEME_INTERMEDIATE2}Select A DLL By Number: {RESET}").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(dlls):
                return dlls[index]
        print(f"\n{THEME_LIGHT_RED}Invalid Selection, Try Again.{RESET}")
        
# =======================
# DLL Injection Using External Injector.exe
# =======================
def call_injector(pid, dll_path):
    #Call The External Injector.exe With Appropriate Command Line Arguments.
    #Usage: Injector.exe --Process-Id <Pid> --Inject <Dll_Path>
    injector_exe = "injector"  # Ensure injector.exe Is In PATH Or In The Current Directory
    cmd = [injector_exe, "--process-id", str(pid), "--inject", dll_path]
    print(f"\n{THEME_INTERMEDIATE2}Calling Injector With Command: {RESET}" + " ".join(cmd))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"\n{THEME_LIGHT_BLUE}Successfully Injected Module!{RESET}")
        print(result.stdout)
        return True
    else:
        print(f"\n{THEME_LIGHT_RED}Injector Failed!{RESET}")
        print(result.stderr)
        return False

def inject_hypno(pid, python_code):
    #Inject Python Code Into A Running Python Process Using The Hypno Tool, with improved error handling.
    try:
        cmd = ["hypno", str(pid), python_code]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"{THEME_LIGHT_BLUE}Hypno Injection Successful.{RESET}")
            print(result.stdout)
            return True
        else:
            error_message = result.stderr
            if "Injector failed with -5" in error_message or "LoadLibrary" in error_message:
                print(f"\n\n{THEME_LIGHT_RED}Hypno Injection Failed: The target process might already have the module injected or there is residual state causing conflicts.{RESET}")
                print(f"{THEME_LIGHT_RED}Error Details: {error_message}{RESET}")
            else:
                print(f"{THEME_LIGHT_RED}Hypno Injection Failed with error: {error_message}{RESET}")
                print(f"\n\n{THEME_LIGHT_RED}Hypno Injection Failed{RESET}")
            return False
    except Exception as e:
        print(f"\n\n{THEME_LIGHT_RED}Unexpected error during Hypno Injection: {e}{RESET}")
        return False

def load_py_file(filename):
    #Load And Parse A Python File Using AST For Validation, Then Return Its Code As A String.
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=filename)
        try:
            code_str = ast.unparse(tree)
        except AttributeError:
            code_str = content
        return code_str
    except Exception as e:
        print(f"{THEME_LIGHT_RED}Error Loading File '{filename}': {e}{RESET}")
        return None
        
# DLL Injection Branch
def dll_injection(pid):
    dll_path = choose_dll()
    print(f"\n{THEME_LIGHT_BLUE}Selected DLL: {dll_path}{RESET}")
    if call_injector(pid, dll_path):
        print(f"{THEME_LIGHT_BLUE}DLL Injection Completed Successfully.{RESET}")
    else:
        print(f"{THEME_LIGHT_RED}DLL Injection Failed.{RESET}")

# ============================
# Suspension-Based EXE Execution
# ============================
def list_exes():
    #List all .exe files in the current directory.
    return [f for f in os.listdir() if f.endswith(".exe")]

def select_exe(exes):
    #Prompt user to select an .exe file.
    if not exes:
        print(f"{THEME_LIGHT_RED}No .exe Files Found In The Current Directory.{RESET}")
        return None
    
    print(f"\n{THEME_INTERMEDIATE3}Select An Executable To Run:{RESET}")
    for i, exe in enumerate(exes, start=1):
        print(f"[{i}] {exe}")

    while True:
        try:
            choice = int(input(f"\n{THEME_INTERMEDIATE2}Enter The Number Of The .exe File: {RESET}"))
            if 1 <= choice <= len(exes):
                return exes[choice - 1]
        except ValueError:
            pass
        print(f"{THEME_LIGHT_RED}Invalid choice. Try again.{RESET}")

def suspend_processes(pid):
    #Suspend a process and all its child processes.
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)  

        print(f"{THEME_INTERMEDIATE3}Suspending Main Process {pid} ({parent.name()}){RESET}")
        parent.suspend()
        
        for child in children:
            try:
                print(f"{THEME_INTERMEDIATE3}Suspending Subprocess {child.pid} ({child.name()}){RESET}")
                child.suspend()
            except psutil.NoSuchProcess:
                pass
    except psutil.NoSuchProcess:
        print(f"{THEME_LIGHT_RED}Main Process No Longer Exists.{RESET}")

def execute_with_suspension():
    #Launches an EXE in a new console, waits for a specified time,
    #suspends the process (and its children), and then prompts the user
    #to choose one of the suspended processes for injection.
    #Returns the PID of the selected process.
    exes = list_exes()
    exe_name = select_exe(exes)
    if not exe_name:
        return None

    try:
        timer = float(input(f"{THEME_INTERMEDIATE2}Enter Time Before Suspension (Seconds): {RESET}").strip())
    except ValueError:
        print(f"{THEME_LIGHT_RED}Invalid Time Entered. Aborting.{RESET}")
        return None

    print(f"\n\n{THEME_INTERMEDIATE3}Launching '{exe_name}' And Suspending After {timer:.2f} Seconds...{RESET}\n")

    # Launch the EXE. On Windows, call the EXE directly to capture its PID.
    if os.name == "nt":  
        process = subprocess.Popen([exe_name], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        process = subprocess.Popen([exe_name])
    
    # Wait for the specified time before suspension.
    time.sleep(timer)
    suspend_processes(process.pid)
    
    # Gather the main process and its children.
    try:
        main_proc = psutil.Process(process.pid)
        children = main_proc.children(recursive=True)
        group = [main_proc] + children
        
        print(f"\n{THEME_INTERMEDIATE3}Suspended Processes In '{exe_name}':{RESET}")
        for idx, proc in enumerate(group, 1):
            try:
                print(f"{THEME_INTERMEDIATE1}{idx}:{RESET} PID: {proc.pid} - Name: {proc.name()}")
            except psutil.NoSuchProcess:
                continue
        
        while True:
            choice = input(f"\n{THEME_INTERMEDIATE2}Select A Process By Number For Injection: {RESET}").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(group):
                    return group[index].pid
            print(f"{THEME_LIGHT_RED}Invalid Selection, Try Again.{RESET}")
    except psutil.NoSuchProcess:
        print(f"{THEME_LIGHT_RED}The launched process no longer exists.{RESET}")
        return None

# ========================
# Main Application Logic
# ========================
def main():
    print_banner()
    print(f"{THEME_INTERMEDIATE3}=== Choose a Function ==={RESET}")
    print(f"{THEME_INTERMEDIATE1}1:{RESET} Process Injection")
    print(f"{THEME_INTERMEDIATE1}2:{RESET} Run EXE and Suspend After Delay")
    
    function_choice = input(f"\n{THEME_INTERMEDIATE2}Make A Selection: {RESET}").strip()
    
    if function_choice == "2":
        target_pid = execute_with_suspension()
        if target_pid is None:
            print(f"{THEME_LIGHT_RED}No Valid Process Selected. Exiting.{RESET}")
            return
    else:
        print(f"\n{THEME_INTERMEDIATE3}=== Process Selection ==={RESET}")
        target_pid = choose_process()
        print(f"\n{THEME_LIGHT_BLUE}Selected Process PID: {target_pid}{RESET}")

    print(f"\n{THEME_INTERMEDIATE3}=== Injection Method ==={RESET}")
    print(f"{THEME_INTERMEDIATE1}1:{RESET} Inject DLL (Using PyInjector x64/x86)")
    print(f"{THEME_INTERMEDIATE1}2:{RESET} Use Hypno (Type/Load Python Code)")
    while True:
        method = input(f"\n{THEME_INTERMEDIATE2}Enter 1 Or 2: {RESET}").strip()
        if method in ("1", "2"):
            break
        print(f"\n{THEME_LIGHT_RED}Invalid Input. Please Enter 1 Or 2.{RESET}")

    if method == "1":
        dll_injection(target_pid)
    else:
        print(f"\n{THEME_LIGHT_BLUE}Enter Python Code To Inject.{RESET}")
        print(f"{THEME_LIGHT_BLUE}Type '!load filename.py' To Load An Entire File, Or '!quit' To Exit.{RESET}\n")
        while True:
            python_input = input(f"{THEME_INTERMEDIATE2}Hypno> {RESET}").strip()
            if python_input.lower() == "!quit":
                print(f"{THEME_LIGHT_BLUE}Exiting Hypno Injection Mode.{RESET}")
                break
            elif python_input.lower().startswith("!load"):
                parts = python_input.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{THEME_DARK_PURPLE}Usage: !Load filename.py{RESET}")
                    continue
                filename = parts[1].strip()
                code_to_inject = load_py_file(filename)
                if code_to_inject is None:
                    continue
                if not inject_hypno(target_pid, code_to_inject):
                    print(f"{THEME_LIGHT_RED}Hypno Injection Failed.{RESET}")
            else:
                if not inject_hypno(target_pid, python_input):
                    print(f"{THEME_LIGHT_RED}Hypno Injection Failed.{RESET}")

if __name__ == "__main__":
    main()
