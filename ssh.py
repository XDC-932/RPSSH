# Copyright (C) 2025 <xdc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
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