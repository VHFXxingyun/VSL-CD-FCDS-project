import serial
import time


def open_serial(port: str, baudrate: int, timeout: float = 1.0, init_delay: float = 2.0):
    """
    打开串口
    """
    ser = serial.Serial(port, baudrate, timeout=timeout)
    time.sleep(init_delay)
    print(f"串口已打开: {port}")
    return ser


def send_command(ser, cmd: str):
    """
    发送一条串口命令
    """
    message = cmd + '\n'
    ser.write(message.encode('utf-8'))


def read_reply(ser):
    """
    读取 ESP32 的两行回复
    返回:
        reply1, reply2
    """
    reply1 = ser.readline().decode('utf-8', errors='ignore').strip()
    reply2 = ser.readline().decode('utf-8', errors='ignore').strip()
    return reply1, reply2


def close_serial(ser):
    """
    关闭串口
    """
    if ser and ser.is_open:
        ser.close()
        print("串口已关闭")
