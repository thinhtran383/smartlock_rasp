import threading
import time

exitEvent = threading.Event()

# Biến cờ để kiểm soát kết thúc luồng


# Hàm thực hiện công việc trong luồng
def print_numbers():
    i = 0
    while not exitEvent.is_set():
        time.sleep(1)
        print(f"Thread 1: {i}")
        i += 1

thread1 = threading.Thread(target=print_numbers)
thread1.start()


def print_abc():
    i = 0
    while True:
        time.sleep(1)
        print(f"Thread 2: {i}")
        i += 1

thread2 = threading.Thread(target=print_abc)
# thread2.start()

time.sleep(5)
exitEvent.set()

