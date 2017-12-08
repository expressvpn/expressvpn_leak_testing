import queue
import re
import subprocess
import threading
import time

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.local_component import LocalComponent

# TODO: This is hacked together quite rapidly but it works. Tidy it up and make it more robust.
# TODO: Stop ngrok from splurging output onto the command line.
class WebServer(LocalComponent):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._server_proc = None
        self._ngrok_proc = None

    def server_main(self, root_folder, port):
        self._server_proc = subprocess.Popen(
            ['python', '-m', 'http.server', str(port)], stdout=None, stderr=None, cwd=root_folder)
        time.sleep(1)
        if self._server_proc.poll():
            raise XVEx("Server failed to start")

    @staticmethod
    def enqueue_ngrok_output(out, theq):
        for line in iter(out.readline, b''):
            theq.put(line)
        out.close()

    def ngrok_main(self, port):
        cmd = ['ngrok', 'http', str(port), '-log', 'stdout', '--log-level', 'debug']
        self._ngrok_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None)
        theq = queue.Queue()
        thread = threading.Thread(
            target=WebServer.enqueue_ngrok_output, args=(self._ngrok_proc.stdout, theq))
        thread.daemon = True # thread dies with the program
        thread.start()

        prog = re.compile(r".*URL:([^\s]+)\s.*")
        while 1:
            try:
                line = theq.get(timeout=1)
                match = prog.match(str(line))
                if not match:
                    continue

                url = match.group(1)
                L.debug("ngrok secure url is {}".format(url))
                return match.group(1)
            except queue.Empty:
                # Add a timeout for getting URL
                pass

    def start_server(self, root_folder, port, https=False):
        if self._server_proc:
            raise XVEx("Server already running")

        self.server_main(root_folder, port)

        if not https:
            return "http://localhost:{}".format(port)

        return self.ngrok_main(port)

    def stop_server(self):
        if self._server_proc:
            self._server_proc.terminate()
            self._server_proc = None

        if self._ngrok_proc:
            self._ngrok_proc.terminate()
            self._ngrok_proc = None
