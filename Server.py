import socket
import json
import select
import datetime
import sqlite3

SERVER_ADDRESS = '127.0.0.1', 54321
MAX_CLIENTS = 100
DB_PATH = 'data.sqlite3'


class Station:
    def __init__(self, addr, sock):
        self.addr = addr
        self.sock = sock


def main():
    station_dict: dict[socket.socket: Station] = {}

    with sqlite3.connect(DB_PATH) as conn:
        with conn:
            conn.execute("""
                    CREATE TABLE IF NOT EXISTS station_status (
                        station_id INT,
                        last_date TEXT,
                        alarm1 INT,
                        alarm2 INT,
                        PRIMARY KEY(station_id)
                    );
                """)

            with socket.socket() as accept_socket:
                accept_socket.bind(SERVER_ADDRESS)
                accept_socket.listen(MAX_CLIENTS)
                print("Server is listening at {}:{}".format(*SERVER_ADDRESS))

                while True:
                    rlist, _, _ = select.select([accept_socket] + list(station_dict), [], [])
                    for sock in rlist:
                        if sock is accept_socket:
                            client_sock, client_addr = accept_socket.accept()
                            print("new client {}:{}".format(*client_addr))
                            new_station = Station(client_addr, client_sock)
                            station_dict[client_sock] = new_station
                        else:
                            station = station_dict[sock]
                            request = sock.recv(1024)
                            if request == b'':
                                del station_dict[sock]
                                sock.close()
                                print("client disconnected {}:{}".format(*station.addr))
                            else:
                                try:
                                    req = request.decode()
                                    req = json.loads(req)
                                    station_id_str = req['ID']
                                    alarm1_str = req['Alarm1']
                                    alarm2_str = req['Alarm2']
                                    resp_str = station_id_str + " " + alarm1_str + " " + alarm2_str
                                    station_id = int(station_id_str)
                                    alarm1 = int(alarm1_str)
                                    alarm2 = int(alarm2_str)
                                except json.JSONDecodeError:
                                    resp_str = 'error: not json'
                                except ValueError:
                                    resp_str = 'error: not integers'
                                last_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                                with conn:
                                    conn.execute("""
                                            INSERT OR REPLACE INTO station_status
                                                VALUES (?, ?, ?, ?);
                                            """, (station_id, last_date, alarm1, alarm2))

                                print("{}:{} -> {}".format(*station.addr, resp_str))


if __name__ == '__main__':
    main()
