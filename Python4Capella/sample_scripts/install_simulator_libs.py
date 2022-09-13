import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("pyyaml")

# TODO: colocar todas as libs a serem instaladas aqui
