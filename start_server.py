import subprocess
import sys
import os

def main():
    # Переходим в папку server и запускаем сервер
    os.chdir('server')
    subprocess.run([sys.executable, 'server.py'])

if __name__ == '__main__':
    main()
