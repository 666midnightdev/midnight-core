#!/bin/bash
# Helper: ensure postgres up, then run msfconsole with piped commands
# Usage: msf-run.sh "use aux/...; set RHOSTS x; run"
pg_ctlcluster 18 main start 2>/dev/null || true
sleep 2
# convert semicolons to newlines so msfconsole treats each as separate command
cmds=$(echo "$1" | tr ';' '\n')
printf '%s\nexit\n' "$cmds" | msfconsole -q 2>/dev/null
