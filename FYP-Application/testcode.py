import subprocess, os
from subprocess import call

def run_program():
    cmd = f"{os.path.dirname(__file__)}/api/extension/main"
    print(cmd)
    if os.access(cmd, os.X_OK):
    #     print('test')
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        a = result.stdout.readlines()
        return a
    # else:
    #     path, file = os.path.split(cmd)
    #     result = subprocess.call(file, shell=True)
    #     return result
if __name__=="__main__":
    print(run_program())