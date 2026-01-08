import time
import os
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from datetime import datetime

console = Console()
LOG_FILE = os.path.expanduser("~/iris_state/sessions/oracle_session_003_run.log")

def generate_table(lines):
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Prompt", width=12)
    table.add_column("Sample", width=8, justify="center")
    table.add_column("Lexical", justify="right")
    table.add_column("Distrib", justify="right")
    table.add_column("Zone", justify="center")
    
    # Parse last 10 relevant lines
    count = 0
    for line in reversed(lines):
        if "[p" in line and "lex=" in line:
            # Example: [p5 6/10] lex=3.036 dist=1.039 [LASER]
            try:
                parts = line.strip().split()
                # p_part -> [p5
                # idx_part -> 6/10]
                prompt_num = parts[0].replace("[p", "")
                sample_idx = parts[1].replace("]", "")
                
                lex_val = parts[2].split("=")[1]
                dist_val = parts[3].split("=")[1]
                zone_val = parts[4] # [LASER]
                
                # Color coding
                dist_float = float(dist_val)
                dist_color = "green"
                if dist_float > 1.5:
                    dist_color = "bold magenta" # Lantern/Void
                elif dist_float < 0.8:
                    dist_color = "red" # Static
                
                zone_color = "white"
                if "LASER" in zone_val: zone_color = "blue"
                if "LANTERN" in zone_val: zone_color = "magenta"
                if "VOID" in zone_val: zone_color = "bold red"

                table.add_row(
                    f"P{prompt_num}", 
                    sample_idx, 
                    lex_val, 
                    f"[{dist_color}]{dist_val}[/]", 
                    f"[{zone_color}]{zone_val}[/]"
                )
                count += 1
                if count >= 8: break
            except:
                continue
                
    return table

def get_current_block(lines):
    for line in reversed(lines):
        if "BLOCK:" in line:
            return line.strip().replace("BLOCK: ", "").replace("=", "").strip()
    return "Initializing..."

def monitor():
    if not os.path.exists(LOG_FILE):
        console.print(f"[red]Log file not found: {LOG_FILE}[/]")
        return

    with Live(refresh_per_second=2) as live:
        while True:
            try:
                with open(LOG_FILE, "r") as f:
                    lines = f.readlines()
                
                current_block = get_current_block(lines)
                table = generate_table(lines)
                
                panel = Panel(
                    table,
                    title=f"[bold yellow]Oracle Session 003 • {current_block}[/]",
                    border_style="blue",
                    padding=(1, 2)
                )
                
                live.update(panel)
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                # console.log(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    console.print(f"[green]Starting Entropy Watcher for {LOG_FILE}...[/]")
    monitor()
