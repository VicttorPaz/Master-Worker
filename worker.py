import socket, threading, time, random, sys

# Configuración del Worker apuntando a la IP correcta del Master
NODE_ID, MASTER_IP, UDP_PORT, TCP_PORT = "worker-01", "192.168.1.6", 5000, 5001

def send_heartbeats():
    """Envía señales de vida periódicas (UDP) al Master."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            msg = f"PING:{NODE_ID} {random.randint(10, 80)}% ACTIVE"
            sock.sendto(msg.encode(), (MASTER_IP, UDP_PORT))
        except: 
            pass
        time.sleep(2)

def tcp_client_connection():
    """Maneja la sesión TCP persistente de Comando y Control con el Master."""
    while True:
        try:
            print(f"[TCP] Intentando conectar con el Master en {MASTER_IP}:{TCP_PORT}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((MASTER_IP, TCP_PORT))
            
            # Registro inicial
            sock.sendall(f"REGISTER:{NODE_ID}".encode())
            print(f"[TCP] Conectado y registrado exitosamente como {NODE_ID}")
            
            while data := sock.recv(1024):
                cmd = data.decode()
                
                # Actividad 2: Ejecutar Tarea
                if cmd.startswith("EXEC_TASK:"):
                    task_content = cmd.split(":", 1)[1]
                    print(f"\n[COMANDO RECIBIDO] Ejecutando tarea: {task_content}")
                    sock.sendall(f"RESULT:{NODE_ID} -> Tarea '{task_content}' OK".encode())
                
                # Actividad 3: Ráfaga de estrés / Broadcast
                elif cmd.startswith("BROADCAST_STRESS:"):
                    parts = cmd.split(":")
                    target = parts[1]
                    duration = parts[2]
                    
                    print(f"\n[¡ALERTA RÁFAGA!] BROADCAST_STRESS recibido.")
                    print(f" -> Objetivo: {target}")
                    print(f" -> Duración: {duration} segundos")
                    
                    # Simulación de la ráfaga
                    print(f" -> [Worker] Ejecutando ráfaga hacia {target} durante {duration}s...")
                    
                    # Respuesta al Master
                    sock.sendall(f"RESULT:{NODE_ID} -> Ráfaga completada hacia {target}".encode())

        except Exception as e:
            print(f"[CONEXIÓN PERDIDA] {e}. Reintentando en 3 segundos...")
            time.sleep(3)

if __name__ == '__main__':
    print(f"--- WORKER: {NODE_ID} ---")
    threading.Thread(target=send_heartbeats, daemon=True).start()
    tcp_client_connection()