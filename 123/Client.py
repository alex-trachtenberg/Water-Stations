import socket
import json
import time

SERVER_ADDRESS = '127.0.0.1', 54321
STATUS_FILE_NAME = "status.txt"
FILE_READ_TIMEOUT = 60


def main():
    with socket.socket() as s:
        s.connect(SERVER_ADDRESS)
        while True:
            with open(STATUS_FILE_NAME, "r") as status_file:
                station_id_str = status_file.readline()[:-1]
                alarm1_str = status_file.readline()[:-1]
                alarm2_str = status_file.readline()
            station_status = {
                'ID': station_id_str,
                'Alarm1': alarm1_str,
                'Alarm2': alarm2_str
            }
            request = json.dumps(station_status).encode()
            s.sendto(request, SERVER_ADDRESS)
            time.sleep(FILE_READ_TIMEOUT)


if __name__ == '__main__':
    main()
