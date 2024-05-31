# СКРИПТ ЗАПУСКАЕТ БОТА НА СЕРВЕРЕ
import cmd
import os
from typing import IO

import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD')


class RunBot(cmd.Cmd):
    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None):
        super().__init__(completekey, stdin, stdout)
        self.root_password = ROOT_PASSWORD
        self.host = HOST
        self.ssh = None

    def do_connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=22, username='root', password=self.root_password)
            self.ssh = ssh
            return {'connected': True}
        except Exception as e:
            return {'connected': False,
                    'message': f'Что-то пошло не так: {e}'}

    def do_run(self):
        try:
            ssh = self.ssh
            ssh.exec_command('cd doskiDyadiJeniBot; killall python3')
            ssh.exec_command("cd doskiDyadiJeniBot; nohup python3 main.py &")
            ssh.exec_command('exit')
            # stdin, stdout, stderr = ssh.exec_command('ps aux | grep python')
            # result = stdout.read()
            # print(result)
            return {'run': True}
        except Exception as e:
            return {'run': False,
                    'message': f'Что-то пошло не так: {e}'}

    # def do_close(self):
    #     ssh = self.connection
    #     ssh.close()


def go():
    run = RunBot()
    run.do_connect()
    response = run.do_run()
    print(response)
    return response['run']


# if __name__ == '__main__':
#     go()
