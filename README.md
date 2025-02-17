# PyInjecto

![PyInjecto](https://i.imgur.com/VsWU8kb.png)

This tool provides a versatile way to inject code into running Python applications. It supports both DLL injection (using an external injector like `injector.exe`) and Python code injection (via the Hypno tool). It also offers the ability to run an executable, suspend it after a delay, and then inject code into the suspended process.

## Features

- **Dynamic Process Selection:**  
  Browse and search running processes by PID or name. Choose a process interactively.

- **DLL Injection:**  
  List available DLLs (prefixed with "pyinjector") in the current directory and inject one into a target process using an external injector.

- **Hypno Python Code Injection:**  
  Inject Python code (or load a Python file) into a running Python process using the Hypno tool.  
  *Supports loading code via `!load filename.py` command.*

- **Executable Launch & Suspension:**  
  Launch an executable, wait for a specified time, suspend the process (and its child processes), then choose a process for injection.
  
--------------------------------------------------

## Configuration & Settings

- Process Selection:  
  Interactive prompts allow you to search for processes by name or PID.

- DLL Selection:  
  Only DLL files with the prefix "pyinjector" are listed for injection.

- Python Code Injection:  
  You can type code directly in the prompt or load a Python file using the "!load" command.

- Executable Suspension:  
  When launching an executable, specify a delay (in seconds) before the process is suspended for injection.

--------------------------------------------------

## Code Structure

- Process Selection Functions:
  - list_running_processes(): Retrieves a list of running processes with their PIDs and names.
  - print_process_list(): Prints the list of running processes.
  - search_processes(): Filters processes based on a keyword.
  - choose_process(): Allows the user to select a process interactively.

- DLL & Hypno Injection Functions:
  - list_dlls(): Lists DLL files in the current directory that match the specified prefix.
  - choose_dll(): Prompts the user to select a DLL.
  - call_injector(): Calls an external injector executable to perform DLL injection.
  - inject_hypno(): Injects Python code into a running process using the Hypno tool.
  - load_py_file(): Loads and validates a Python file (using AST parsing) to retrieve its code.

- Executable Suspension Functions:
  - list_exes(): Lists all .exe files in the current directory.
  - select_exe(): Prompts the user to select an executable file.
  - suspend_processes(): Suspends a process and all its child processes.
  - execute_with_suspension(): Launches an executable, waits for a specified delay, suspends it, and allows selection of a process for injection.

- Main Application Logic:
  Integrates the above components to provide an interactive injection tool that supports both DLL and Python code injection.
