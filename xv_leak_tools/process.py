import subprocess

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class XVProcessException(XVEx):

    def __init__(self, cmd, retcode, stdout, stderr):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout if stdout else "<no output>"
        self.stderr = stderr if stderr else "<no output>"
        super().__init__(self._msg())

    def _msg(self):
        return "Subprocess execution failed: cmd: {}, retcode: {}, stdout: {}, stderr: {}".format(
            self.cmd, self.retcode, self.stdout, self.stderr)

def execute_subprocess(cmd):
    L.verbose("execute_subprocess: Executing command: {}".format(' '.join(cmd)))
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    retcode = process.wait()
    try:
        return retcode, stdout.decode(), stderr.decode()
    except UnicodeDecodeError:
        return retcode, stdout.decode('cp1252'), stderr.decode('cp1252')

def check_subprocess(cmd):
    retcode, stdout, stderr = execute_subprocess(cmd)
    if retcode == 0:
        return stdout, stderr

    raise XVProcessException(cmd, retcode, stdout, stderr)

# def loop_process(cmd, loop_timeout, process_timeout=1):
#     t_start = time.time()
#     while time.time() - t_start < loop_timeout:
#         L.debug("Executing command: {}".format(' '.join(cmd)))
#         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         time.sleep(process_timeout)
#         retcode = process.poll()
#         if retcode:
#             raise XVEx("Command '{}' returned non-zero exit status {}" .format(
#                 ', '.join(cmd), retcode))
#         elif retcode == 0:
#             L.debug("Command succeeded")
#             return True
#         else:
#             process.terminate()
#     return False
