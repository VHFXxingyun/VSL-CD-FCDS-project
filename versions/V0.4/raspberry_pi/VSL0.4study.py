import serial          # 导入 pyserial 库，用于串口通信
import time            # 导入 time 库，用于延时

# 串口设备名
# 树莓派通过 USB 连接 ESP32 后，系统通常会识别成 /dev/ttyUSB0
PORT = '/dev/ttyUSB0'

# 波特率，必须和 ESP32 端 Serial.begin(115200) 一致
BAUDRATE = 115200

# 读取串口时的超时时间（秒）
SERIAL_TIMEOUT = 1

# 打开串口后等待设备稳定的时间（秒）
INIT_DELAY = 2

# 特殊命令集合
# 这些命令不是数值增量命令，而是直接触发某个固定动作
SPECIAL_COMMANDS = {'HOME', 'OUT'}


def open_serial():
    """打开串口"""
    # 创建并打开一个串口对象
    # timeout=SERIAL_TIMEOUT 表示读取时最多等待 1 秒
    ser = serial.Serial(PORT, BAUDRATE, timeout=SERIAL_TIMEOUT)

    # 给串口设备一点初始化时间，避免刚打开时通信不稳定
    time.sleep(INIT_DELAY)

    # 打印提示信息
    print(f"串口已打开: {PORT}")

    # 把打开好的串口对象返回给调用者
    return ser


def send_command(ser, cmd: str):
    """发送一条串口命令"""
    # 在命令末尾加一个换行符 '\n'
    # 因为 ESP32 端是按“读一整行”的方式接收命令
    message = cmd + '\n'

    # 把 Python 字符串编码成 utf-8 字节后通过串口发送
    ser.write(message.encode('utf-8'))

    # 在本地终端打印已发送的命令，便于调试
    print("已发送:", cmd)


def read_reply(ser):
    """读取 ESP32 的两行回复"""
    # 从串口读取第一行
    # readline() 会一直读到换行符 '\n' 或超时为止
    # decode(...) 把字节解码成字符串
    # strip() 去掉首尾空格、换行符等
    reply1 = ser.readline().decode('utf-8', errors='ignore').strip()

    # 从串口读取第二行
    reply2 = ser.readline().decode('utf-8', errors='ignore').strip()

    # 如果第一行有内容，就打印
    if reply1:
        print("收到:", reply1)

    # 如果第二行有内容，就打印
    if reply2:
        print("收到:", reply2)


def is_valid_increment_command(cmd: str) -> bool:
    """
    检查是否为合法格式:
    +15,-24
    0,+10
    -8,0
    """
    # 按英文逗号分割命令
    # 例如 "+15,-24" -> ["+15", "-24"]
    parts = cmd.split(',')

    # 如果分割后不是两部分，说明格式不对
    if len(parts) != 2:
        return False

    # 取出第一个值，表示 pan_delta
    # strip() 是为了防止用户输入了多余空格
    pan_str = parts[0].strip()

    # 取出第二个值，表示 tilt_delta
    tilt_str = parts[1].strip()

    # 如果其中任一部分为空字符串，也是不合法的
    if len(pan_str) == 0 or len(tilt_str) == 0:
        return False

    try:
        # 尝试把 pan_str 转成整数
        # 合法示例：+15、-24、0
        int(pan_str)

        # 尝试把 tilt_str 转成整数
        int(tilt_str)
    except ValueError:
        # 只要有一个无法转换成整数，就说明格式非法
        return False

    # 通过所有检查，说明是合法命令
    return True


def main():
    # 先定义一个串口对象变量，初始为空
    ser = None

    try:
        # 打开串口
        ser = open_serial()

        # 进入无限循环，不断接收用户输入
        while True:
            # 从终端读取一行输入
            # strip() 去掉两端空格
            cmd = input("输入命令(+15,-24 / HOME / OUT)(输入 q 退出): ").strip()

            # 如果用户直接按回车，跳过本轮循环
            if not cmd:
                continue

            # 转成大写，方便统一判断特殊命令
            # 例如 home -> HOME
            cmd_upper = cmd.upper()

            # 如果输入 q，则退出程序
            if cmd_upper == 'Q':
                print("退出程序")
                break

            # 如果输入的是特殊命令 HOME 或 OUT
            if cmd_upper in SPECIAL_COMMANDS:
                # 发送特殊命令
                send_command(ser, cmd_upper)

                # 读取 ESP32 回复
                read_reply(ser)

                # 继续下一轮输入
                continue

            # 如果输入的是数值增量命令，例如 +15,-24
            if is_valid_increment_command(cmd):
                # 发送原始命令
                # 这里不用 cmd_upper，因为数值和符号不需要转大写
                send_command(ser, cmd)

                # 读取 ESP32 回复
                read_reply(ser)
            else:
                # 如果既不是特殊命令，也不是合法增量命令，就提示错误
                print("无效命令格式。")
                print("正确示例: +15,-24")
                print("或输入: HOME / OUT / q")

    except Exception as e:
        # 捕获运行中出现的异常，例如串口打开失败
        print("出错:", e)

    finally:
        # 无论程序正常退出还是异常退出，最后都尝试关闭串口
        if ser and ser.is_open:
            ser.close()
            print("串口已关闭")


# 只有当这个 py 文件被直接运行时，才执行 main()
if __name__ == '__main__':
    main()
