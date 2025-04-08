import paramiko
import time

recv_buf = 16384

class SSH():
    def __init__(self, win, ip, username='root', password='root'):
        try:
            self.ip = ip
            self.username = username
            self.password = password
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.username, password=self.password)
            self.ssh = self.client.invoke_shell()
            win.ssh = self
            self.ssh.settimeout(1)

            time.sleep(0.5)
            if self.ssh.recv_ready():
                self.ssh.recv(recv_buf)  # 丢弃欢迎信息
        except Exception as e:
            print(f"Connection failed: {e}")
            self.client.close()
            raise e

    def tx_cmd(self, cmd):
        try:
            self.ssh.send(cmd + "\n")
            time.sleep(0.5)
            output = ""
            while self.ssh.recv_ready():
                output += self.ssh.recv(recv_buf).decode("utf-8")
            
            # 去除命令和提示符
            lines = output.splitlines()
            filtered_output = []
            for line in lines:
                # 跳过包含命令或提示符的行
                if cmd in line or line.startswith("root@"):
                    continue
                # 删除第二列数据
                columns = line.split()  # 按空格分割列
                if columns:  # 确保行不为空
                    filtered_output.append(columns[0])  # 仅保留第一列
            return "\n".join(filtered_output).strip()
        except Exception as e:
            print(f"Command execution failed: {e}")
            raise e