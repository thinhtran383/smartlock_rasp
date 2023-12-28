import threading
import time

stopThread = False
stopThread2 = False

def myFunction():
    global stopThread, stopThread2
    while not stopThread:
        print('Running 1...')
        time.sleep(1)
    print('Thread 1 stopped.')

def myFunction2():
    global stopThread, stopThread2
    while not stopThread2:
        print('Running 2...')
        time.sleep(1)
    print('Thread 2 stopped.')

# Tạo và bắt đầu luồng 1
myThread = threading.Thread(target=myFunction, daemon=True)
myThread.start()

# Tạo và bắt đầu luồng 2
myThread2 = threading.Thread(target=myFunction2, daemon=True)
myThread2.start()

# Chờ 3 giây để luồng 1 chạy
time.sleep(3)

# Dừng cả hai luồng
stopThread = True
stopThread2 = True

# Chờ đến khi cả hai luồng đều dừng
myThread.join()
myThread2.join()

# Bắt đầu lại luồng 1 nếu nó đã dừng
if not myThread.is_alive():
    stopThread = False
    myThread = threading.Thread(target=myFunction, daemon=True)
    myThread.start()

    # Chờ 3 giây để luồng 1 chạy
    time.sleep(3)

    # Dừng luồng 1
    stopThread = True

    # Chờ đến khi luồng 1 dừng
    myThread.join()

print('Main thread is done.')
