#!/bin/sh
# Controlled network impairment for the physical experiment (Linux, needs root).
# Usage: sudo ./netem_impair.sh <iface> <loss_pct> <delay_ms> <jitter_ms>   |   sudo ./netem_impair.sh <iface> clear
IF="$1"
if [ "$2" = "clear" ]; then tc qdisc del dev "$IF" root 2>/dev/null; exit 0; fi
tc qdisc replace dev "$IF" root netem loss "$2"% delay "$3"ms "$4"ms distribution normal
tc qdisc show dev "$IF"
