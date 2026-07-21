import os
import sys
import io
import json
import requests
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.box import SIMPLE

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console = Console(
    force_terminal=True,
    width=120,
    markup=True,
    emoji=True,
    legacy_windows=False
)

BANNER_ART = r"""
       ___                                     ___                       ___           ___                   
     /\  \                     _____         /\  \                     /\__\         /\  \                  
    |::\  \       ___         /::\  \        \:\  \       ___         /:/ _/_        \:\  \         ___     
    |:|:\  \     /\__\       /:/\:\  \        \:\  \     /\__\       /:/ /\  \        \:\  \       /\__\    
  __|:|\:\  \   /:/__/      /:/  \:\__\   _____\:\  \   /:/__/      /:/ /::\  \   ___ /::\  \     /:/  /    
 /::::|_\:\__\ /::\  \     /:/__/ \:|__| /::::::::\__\ /::\  \     /:/__\/\:\__\ /\  /:/\:\__\   /:/__/     
 \:\~~\  \/__/ \/\:\  \__  \:\  \ /:/  / \:\~~\~~\/__/ \/\:\  \__  \:\  \ /:/  / \:\/:/  \/__/  /::\  \     
  \:\  \        ~~\:\/\__\  \:\  /:/  /   \:\  \        ~~\:\/\__\  \:\  /:/  /   \::/__/      /:/\:\  \    
   \:\  \          \::/  /   \:\/:/  /     \:\  \          \::/  /   \:\/:/  /     \:\  \      \/__\:\  \   
    \:\__\         /:/  /     \::/  /       \:\__\         /:/  /     \::/  /       \:\__\          \:\__\  
     \/__/         \/__/       \/__/         \/__/         \/__/       \/__/         \/__/           \/__/
"""

PENTAGRAM_ART = ""

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "midnight-agent"
MODEL_DISPLAY = "Midnight Agent (Mistral NeMo 12B)"

context_buffer = ""
conversation_history = []

WSL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_wsl_command",
            "description": "Execute a terminal command inside the default Kali Linux WSL distribution. Use this tool whenever the user asks you to run a security tool, network check, list files, or execute any Linux shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact shell command to execute in Kali Linux (e.g. 'nmap -F 127.0.0.1', 'whoami', 'uname -a', 'ls -la')."
                    }
                },
                "required": ["command"]
            }
        }
    }
]


def print_initial_screen():
    console.clear()
    console.print(Text(BANNER_ART, style="bold #DC143C"))
    logo_line = Text()
    logo_line.append(Text(PENTAGRAM_ART, style="bold #DC143C"))
    logo_line.append("   ")
    model_text = Text()
    model_text.append("\n\n\n\n\n")
    model_text.append("Model", style="dim #666666")
    model_text.append("\n")
    model_text.append(MODEL_DISPLAY, style="bold #FFFFFF")
    model_text.append("\n\n")
    model_text.append("Local", style="dim #666666")
    model_text.append("\n")
    model_text.append("Ollama API", style="#FFFFFF")
    logo_line.append(model_text)
    console.print(logo_line)
    console.print(Text("-" * 80, style="dim #333333"))


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[ERROR] File not found: {path}"
    except Exception as e:
        return f"[ERROR] Failed to read file: {e}"


def list_directory(path: str) -> str:
    try:
        items = os.listdir(path)
        result = []
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result.append(f"[DIR]  {item}/")
            else:
                size = os.path.getsize(full_path)
                result.append(f"[FILE] {item} ({size} bytes)")
        return "\n".join(result) if result else "(empty)"
    except FileNotFoundError:
        return f"[ERROR] Directory not found: {path}"
    except Exception as e:
        return f"[ERROR] Failed to list directory: {e}"


def handle_special_commands(user_input: str) -> bool:
    global context_buffer
    parts = user_input.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd == "/read" and len(parts) > 1:
        path = parts[1].strip()
        content = read_file(path)
        context_buffer = f"Here is the content of the file '{path}':\n\n{content}\n\n"
        console.print(Panel(f"[green]File loaded:[/green] {path}", border_style="green", box=SIMPLE))
        return True

    if cmd == "/dir" and len(parts) > 1:
        path = parts[1].strip()
        content = list_directory(path)
        context_buffer = f"Here is the directory listing for '{path}':\n\n{content}\n\n"
        console.print(Panel(f"[green]Directory loaded:[/green] {path}", border_style="green", box=SIMPLE))
        return True

    return False


def execute_wsl_command(command: str) -> str:
    try:
        result = subprocess.run(
            ["wsl", "-d", "kali-linux", "bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return output if output.strip() else "(No output returned)"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out after 120 seconds."
    except Exception as e:
        return f"[ERROR] Failed to execute command: {e}"


def stream_ollama(messages: list) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": WSL_TOOLS,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
        
        if response.status_code == 404:
            console.print(f"\n[bold yellow]Model '{MODEL}' tidak ditemukan.[/bold yellow]")
            console.print("[cyan]Silakan buat model terlebih dahulu di terminal menggunakan perintah:[/cyan]")
            console.print(f"[bold white]  ollama create {MODEL} -f ./Modelfile[/bold white]\n")
            return ""
            
        response.raise_for_status()

        full_response = ""
        tool_calls = []

        with Live(console=console, refresh_per_second=15) as live:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    message = data.get("message", {})
                    
                    # Accumulate content
                    chunk = message.get("content", "")
                    if chunk:
                        full_response += chunk
                        live.update(Markdown(full_response, code_theme="monokai"))
                    
                    # Accumulate tool calls
                    if "tool_calls" in message:
                        for tc in message["tool_calls"]:
                            idx = tc.get("index", 0)
                            while len(tool_calls) <= idx:
                                tool_calls.append({"function": {"name": "", "arguments": ""}})
                            
                            if "function" in tc:
                                fn = tc["function"]
                                if "name" in fn and fn["name"]:
                                    tool_calls[idx]["function"]["name"] += fn["name"]
                                if "arguments" in fn and fn["arguments"]:
                                    if isinstance(fn["arguments"], str):
                                        tool_calls[idx]["function"]["arguments"] += fn["arguments"]
                                    elif isinstance(fn["arguments"], dict):
                                        tool_calls[idx]["function"]["arguments"] = fn["arguments"]
                    
                    if data.get("done", False):
                        break

        # Parse string arguments if any
        for tc in tool_calls:
            args = tc["function"].get("arguments", "")
            if isinstance(args, str) and args.strip():
                try:
                    tc["function"]["arguments"] = json.loads(args)
                except json.JSONDecodeError:
                    pass

        # Handle tool calls if any
        if tool_calls:
            for tc in tool_calls:
                func_name = tc["function"].get("name")
                args = tc["function"].get("arguments", {})
                
                if func_name == "execute_wsl_command":
                    command = args.get("command", "")
                    
                    console.print(Panel(f"[yellow]AI ingin mengeksekusi perintah di Kali Linux WSL:[/yellow]\n[bold cyan]{command}[/bold cyan]", title="Permintaan Eksekusi Alat", border_style="yellow"))
                    
                    # Security confirmation prompt
                    confirm = console.input("[bold red]Apakah Anda mengizinkan perintah ini dijalankan? (y/n): [/bold red]").strip().lower()
                    
                    if confirm in ("y", "yes"):
                        console.print("[yellow]Mengeksekusi perintah di Kali Linux WSL...[/yellow]")
                        output = execute_wsl_command(command)
                        
                        # Display preview of output
                        preview = output[:800] + "\n..." if len(output) > 800 else output
                        console.print(Panel(preview, title="Hasil Output WSL", border_style="green", box=SIMPLE))
                        
                        # Add tool call and tool result to messages history
                        assistant_message = {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": func_name,
                                        "arguments": args
                                    }
                                }
                            ]
                        }
                        tool_message = {
                            "role": "tool",
                            "content": output
                        }
                        
                        messages.append(assistant_message)
                        messages.append(tool_message)
                        
                        # Recursively call stream_ollama with the updated messages
                        return stream_ollama(messages)
                    else:
                        console.print("[red]Eksekusi dibatalkan oleh pengguna.[/red]")
                        
                        assistant_message = {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": func_name,
                                        "arguments": args
                                    }
                                }
                            ]
                        }
                        tool_message = {
                            "role": "tool",
                            "content": "[ERROR] User denied permission to run this command."
                        }
                        messages.append(assistant_message)
                        messages.append(tool_message)
                        
                        # Recursively call stream_ollama so the model knows the command failed
                        return stream_ollama(messages)

        return full_response

    except requests.exceptions.ConnectionError:
        console.print("[bold red]Error: Tidak dapat terhubung ke Ollama di http://localhost:11434[/bold red]")
        console.print("[cyan]Pastikan Ollama sedang berjalan: ollama serve[/cyan]")
        return ""
    except requests.exceptions.Timeout:
        console.print("[bold red]Error: Permintaan ke Ollama habis waktu (timeout)[/bold red]")
        return ""
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        return ""


def main():
    global context_buffer, conversation_history

    print_initial_screen()

    while True:
        try:
            user_input = console.input("[bold #DC143C]root@midnight:~#[/bold #DC143C] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "/exit", "/quit"):
                break

            if user_input.lower() == "/clear":
                context_buffer = ""
                conversation_history = []
                print_initial_screen()
                continue

            if handle_special_commands(user_input):
                continue

            console.print(f"\n[dim]  \u25b2 You[/dim]")
            console.print(f"  {user_input}")
            console.print(f"\n[dim]  \u25bc Assistant[/dim]")

            # Prepare active messages for this turn
            active_messages = []
            
            if context_buffer:
                active_messages.append({"role": "system", "content": context_buffer})
                context_buffer = ""

            active_messages.extend(conversation_history)
            active_messages.append({"role": "user", "content": user_input})

            response = stream_ollama(active_messages)

            if response:
                # Calculate what new messages were added
                system_offset = 1 if (active_messages and active_messages[0]["role"] == "system") else 0
                new_msgs = active_messages[system_offset + len(conversation_history):]
                
                conversation_history.extend(new_msgs)
                conversation_history.append({"role": "assistant", "content": response})

                # Limit history size to 30 messages to avoid prompt bloat
                if len(conversation_history) > 30:
                    conversation_history = conversation_history[-20:]

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted[/dim]")
        except EOFError:
            break


if __name__ == "__main__":
    main()

