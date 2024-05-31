import cmd
import glob
import os
from pathlib import Path
from typing import IO
import paramiko
from dotenv import load_dotenv
from paramiko.client import SSHClient
from scp import SCPClient

load_dotenv()
HOST = os.getenv('HOST')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD')
ROOT_PATH = os.getenv('ROOT_PATH')


class AddData(cmd.Cmd):
    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None):
        super().__init__(completekey, stdin, stdout)
        self.destination = ROOT_PATH
        self.root_password = ROOT_PASSWORD
        self.host = HOST
        self.ssh = None
        self.data_dir = 'doskiDyadiJeniBot'

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

    def add_data(self):
        try:
            # путь к локальной папке
            path_to_dir = Path(__file__).parent.absolute()
            src = path_to_dir
            ssh = self.ssh
            # вывели папки
            stdin, stdout, stderr = ssh.exec_command('ls')
            result = stdout.read().decode("utf-8")
            if self.data_dir in result:
                print(result)
                return {'added': False,
                        'messade': 'Данные уже добавлены'}
            else:
                path_to_dir = Path(__file__).parent.absolute()
                src = path_to_dir
                ssh = SSHClient()
                ssh.load_system_host_keys()
                ssh.connect(self.host, username='root', password=self.root_password, look_for_keys=False)

                with SCPClient(ssh.get_transport()) as scp:
                    files = glob.glob('../doskiDyadiJeniBot/*', recursive=True)
                    ssh.exec_command('mkdir doskiDyadiJeniBot')
                    scp.put('.env', remote_path='/root/doskiDyadiJeniBot')
                    scp.put('.gitignore', remote_path='/root/doskiDyadiJeniBot')


                    for file in files:
                        scp.put(file, remote_path='/root/doskiDyadiJeniBot', recursive=True)

                    print('Added!')

                    scp.close()

                # ssh.exec_command('sudo apt install python3-pip')
                # ssh.exec_command('pip3 install -U pip')
                # ssh.exec_command('pip3 install -r requirements.txt')

                return {'added': True}
        except Exception as e:
            return {'added': False,
                    'message': f'Что-то пошло не так: {e}'}

    # def do_close(self):
    #     ssh = self.ssh
    #     ssh.close()


def add():
    add = AddData()
    add.do_connect()
    response = add.add_data()
    print(response)
    return response['added']

#
# if __name__ == '__main__':
#     add()
