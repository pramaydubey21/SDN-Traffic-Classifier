# SDN Traffic Classification System

## Problem Statement
An SDN-based Traffic Classification System using Mininet and POX controller
that classifies network traffic by type (ICMP, TCP/HTTP, UDP) and applies
different flow rules — allowing, blocking, or prioritizing traffic accordingly.

## Tools Used
- Mininet 2.3.0
- POX Controller 0.7.0
- Open vSwitch
- iperf
- Python 3.10

## Topology
- 1 Switch (s1)
- 4 Hosts:
  - h1 (10.0.0.1) — HTTP client
  - h2 (10.0.0.2) — HTTP server
  - h3 (10.0.0.3) — UDP source
  - h4 (10.0.0.4) — Blocked host

## Setup and Execution

### 1. Install dependencies
```bash
sudo apt install mininet -y
pip3 install ryu
git clone https://github.com/noxrepo/pox
```

### 2. Start POX controller (Terminal 1)
```bash
cd ~/pox
python3 pox.py log.level --DEBUG traffic_classifier
```

### 3. Start Mininet topology (Terminal 2)
```bash
cd ~/sdn_project
sudo python3 topology.py
```

## Test Scenarios

### Scenario 1 — Allowed vs Blocked
```bash
h1 ping -c 3 h2   # Expected: 0% packet loss
h4 ping -c 3 h2   # Expected: 100% packet loss
```

### Scenario 2 — Traffic Classification
```bash
h2 python3 -m http.server 80 &
h1 curl http://10.0.0.2        # HTTP classified as HIGH PRIORITY
h2 iperf -s -u &
h3 iperf -c 10.0.0.2 -u -t 5  # UDP classified and logged
```

## Expected Output
- ICMP traffic → ALLOWED
- HTTP traffic (port 80) → HIGH PRIORITY
- UDP traffic → LOGGED and allowed
- Traffic from h4 → BLOCKED (drop rule installed)

## Flow Table
```bash
sh ovs-ofctl dump-flows s1
```

## References
1. Mininet - http://mininet.org
2. POX Controller - https://github.com/noxrepo/pox
3. OpenFlow 1.0 Specification
