#!/usr/bin/env python3
"""
Tunnel proxy - resolves DNS manually, connects to cloudflare edge,
and proxies SSH traffic through it.
"""
import socket
import ssl
import sys
import threading
import time

HOSTNAME = "pope-operating-ranked-storage.trycloudflare.com"
CLOUDFLARE_EDGE_IP = "104.16.231.132"
LOCAL_PORT = 2222
REMOTE_PORT = 22

def resolve_cloudflare(hostname):
    """Resolve via Python socket (bypasses broken Android DNS)"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"[DNS] {hostname} -> {ip}")
        return ip
    except Exception as e:
        print(f"[DNS] Failed: {e}")
        return None

def proxy_connection(client_sock, edge_ip, hostname):
    """Forward TCP traffic through cloudflare edge"""
    try:
        # Connect to cloudflare edge
        remote = socket.create_connection((edge_ip, 443), timeout=15)
        
        # TLS wrap with SNI
        ctx = ssl.create_default_context()
        tls = ctx.wrap_socket(remote, server_hostname=hostname)
        
        print(f"[PROXY] Connected to edge, forwarding...")
        
        # Proxy data both ways
        def forward(src, dst, name):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except:
                pass
            try: src.close()
            except: pass
            try: dst.close()
            except: pass
        
        t1 = threading.Thread(target=forward, args=(client_sock, tls, "client->edge"))
        t2 = threading.Thread(target=forward, args=(tls, client_sock, "edge->client"))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        t1.join(timeout=300)
        t2.join(timeout=300)
        
    except Exception as e:
        print(f"[PROXY] Error: {e}")
        try: client_sock.close()
        except: pass

def main():
    edge_ip = resolve_cloudflare(HOSTNAME)
    if not edge_ip:
        # Fallback to known IP
        edge_ip = CLOUDFLARE_EDGE_IP
        print(f"[DNS] Using fallback IP: {edge_ip}")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', LOCAL_PORT))
    server.listen(5)
    
    print(f"[LISTEN] SSH proxy on 127.0.0.1:{LOCAL_PORT}")
    print(f"[TARGET] {HOSTNAME}:{REMOTE_PORT} via edge {edge_ip}")
    print(f"[SSH] ssh appveyor@127.0.0.1 -p {LOCAL_PORT}")
    
    while True:
        client, addr = server.accept()
        print(f"[CONN] New connection from {addr}")
        t = threading.Thread(target=proxy_connection, args=(client, edge_ip, HOSTNAME))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    main()
