#!/usr/bin/env python
"""Direct MUD connection test (no GUI)."""

import socket
import time

HOST = "reinosdeleyenda.com"
PORT = 23

print(f"[TEST] Connecting to {HOST}:{PORT}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((HOST, PORT))
    print(f"[TEST] Connected!")

    # Send GMCP negotiation
    iac_do_gmcp = bytes([255, 253, 201])
    sock.sendall(iac_do_gmcp)
    print(f"[TEST] GMCP negotiation sent")

    # Try to receive initial data
    print(f"[TEST] Waiting for server response...")
    for i in range(5):
        try:
            data = sock.recv(4096)
            if data:
                print(f"[TEST] Received {len(data)} bytes:")
                print(repr(data[:200]))
                print(data[:200].decode('utf-8', errors='replace'))
            else:
                print(f"[TEST] Server closed connection")
                break
        except socket.timeout:
            print(f"[TEST] Timeout {i+1}/5")
        time.sleep(1)

    sock.close()
    print(f"[TEST] Closed")
except Exception as e:
    print(f"[TEST] Error: {e}")
    import traceback
    traceback.print_exc()
