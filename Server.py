import socket
import json
import select

SERVER_ADDRESS = '127.0.0.1', 54321
MAX_CLIENTS = 16


class Station:
    def __init__(self, addr, sock):
        self.addr = addr
        self.sock = sock


def main():
    station_dict: dict[socket.socket: Station] = {}

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
                    print("{}:{} -> {}".format(*station.addr, request))
                    if request == b'':
                        del station_dict[sock]
                        sock.close()
                        print("client disconnected {}:{}".format(*station.addr))
                    else:
                        response = calculate_response(request)
                        print("{}:{} -> {}".format(*station.addr, response))
                        station.sock.send(response)


def calculate_response(req: bytes) -> bytes:
    try:
        req = req.decode()
        req = json.loads(req)
        station_id_str = req['ID']
        alarm1_str = req['Alarm1']
        alarm2_str = req['Alarm2']
        resp_str = station_id_str + " " + alarm1_str + " " + alarm2_str
    except UnicodeDecodeError:
        resp_str = 'error: not UTF8'
    except json.JSONDecodeError:
        resp_str = 'error: not json'
    except KeyError:
        resp_str = 'error: invalid message'
    except TypeError:
        resp_str = 'error: invalid message'
    return resp_str.encode()


if __name__ == '__main__':
    main()
