 Taller de Sockets (Master-Worker)

# Universidad Politécnica Salesiana

# Victor Paz, Gabriela Diaz, Sebastian Vilaña
 
# Sistemas Distribuidos  
 


---

## 1. Instrucciones de Ejecución

Para iniciar la arquitectura distribuida en una red local o en un entorno virtualizado, sigue los comandos exactos a continuación:

### Paso 1: Configuración de Red Inicial
Asegúrate de que la dirección IP configurada en `master.py` y `worker.py` corresponda a la interfaz de red del equipo central (en nuestro entorno: `192.168.1.6`).

### Paso 2: Levantar el Nodo Central (Master)
Ejecuta el servidor central desde la terminal principal. Esto iniciará los puertos UDP `5000` y TCP `5001`:

```bash
python master.py
```

### Paso 3: Conectar Múltiples Workers Concurrentes
Abre terminales independientes (en el mismo equipo o en máquinas de la red virtual) y ejecuta cada nodo asignándole un identificador único:

```bash
# En la Terminal 2:
python worker.py worker-01

# En la Terminal 3:
python worker.py worker-02

# En la Terminal 4:
python worker.py worker-03
```

---

## 2. Descripción del Protocolo de Comunicación

El protocolo de la arquitectura se compone de dos canales independientes según el nivel de confiabilidad requerido:

### A. Canal UDP (Latidos / Heartbeats) - Puerto 5000


* **Trama de Envío (Worker -> Master):** `PING:<node_id> <cpu>% <status>`
  * *Ejemplo:* `PING:worker-01 45% ACTIVE`
* **Trama de Respuesta (Master -> Worker):** `ACK`
* **Mecanismo de Desconexión:** El Master mantiene una marca de tiempo (*timestamp*) por cada Worker. Si un Worker no transmite latidos por más de **6 segundos**, se marca automáticamente como `CAÍDO` y sus sockets son destruidos.

---

### B. Canal TCP (Comando y Control Persistente) - Puerto 5001
                     

* **Sintaxis de Comandos (Master -> Worker):**
  * `REGISTER:<node_id>` (Handshake inicial del Worker).
  * `EXEC_TASK:scan_ports`
  * `EXEC_TASK:FETCH_LOGS`
  * `BROADCAST_STRESS:<ip:puerto>:<duracion_segundos>`
* **Sintaxis de Respuestas (Worker -> Master):**
  * `RESULT:<node_id> -> <resultado_de_ejecucion>`

---

## 3. Evidencias de Funcionamiento (Console Logs)

A continuación se presentan los registros de consola que verifican el cumplimiento de los 3 escenarios clave exigidos:

### Evidencia 1: Registro Exitoso de Workers mediante UDP y TCP
Muestra cómo los Workers se registran dinámicamente tanto en la tabla de latidos UDP como en la sesión persistente TCP.

<img width="480" height="195" alt="imagen" src="https://github.com/user-attachments/assets/dd19ca3d-ae81-4229-860b-f99764c8b26d" />
<img width="500" height="164" alt="imagen" src="https://github.com/user-attachments/assets/005b5175-bcd5-4f7f-8bfc-7c4f4585b28f" />

### Evidencia 2: Detección Automática de Caída por Falta de Latidos UDP
Muestra el comportamiento del monitor del Master cuando se apaga abruptamente el proceso del nodo `worker-01 & worker-02`.

<img width="483" height="153" alt="imagen" src="https://github.com/user-attachments/assets/5b7ec579-ccdc-4678-9494-ef43c129618d" />


### Evidencia 3: Ejecución de Comandos en Vivo desde el Master hacia Workers (TCP)
Demuestra el envío de una orden individual (`scan_ports`) y la recepción en tiempo real de los resultados.

**Consola del Master:**

<img width="689" height="364" alt="imagen" src="https://github.com/user-attachments/assets/212a1499-01bb-4b8d-b934-181ab5a21fde" />

<img width="701" height="369" alt="imagen" src="https://github.com/user-attachments/assets/f8032f30-f6db-4112-9619-1d42d4a0f1cc" />

**Consola del Worker :**

<img width="666" height="208" alt="imagen" src="https://github.com/user-attachments/assets/fc939100-5bb7-47b8-aab6-974e35681677" />

<img width="612" height="179" alt="imagen" src="https://github.com/user-attachments/assets/3c38d085-e47b-42b8-8740-400f3b945052" />

