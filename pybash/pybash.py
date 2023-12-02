
# %%
import subprocess
import threading
import queue
import time


class BashInterface:
    def __init__(self):
        self.process = subprocess.Popen(
            ["bash"], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True )
        
        self.output_queue = queue.Queue()
        self.read_available = False
        self.io_thread = threading.Thread(target=self._io_loop)
        self.running = True
        self.io_thread.start()

    def __del__(self):
        self.running = False
        if self.io_thread.is_alive():
            self.io_thread.join()
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait()

    def write_command(self, command):
        if self.process.poll() is not None:
            raise Exception("Bash process has terminated")
        self.process.stdin.write(command + '&& echo pybash_success || echo pybash_fail \n')
        self.process.stdin.flush()

    def read_output(self):
        try:
            if (not self.read_available):
                raise Exception("No data available to read")
            self.read_available = False
            output = []
            while (self.output_queue.qsize() != 0):
                output.append(self.output_queue.get())
            return output
        except Exception as e:
            return None

    def _io_loop(self):
        while self.running:
            output = self.process.stdout.readline()
            if output:
                self.output_queue.put(output)
                if ('pybash_success' in output) or ('pybash_fail' in output):
                    print("Successfully_read")
                    self.read_available = True
            else:
                break


## TO DO : Add timeout decorator for commands

# %%
if __name__ == "__main__":
    bash_interface = BashInterface()

    try:
        command_handover = False
        while True:
            if (not command_handover):
                input_cmd  = input("Input CMD :")
                command_handover = True
                if input_cmd:
                    if (input_cmd == 'exit'):
                        break
                    bash_interface.write_command(input_cmd)

            time.sleep(0.01)

            output = bash_interface.read_output()
            if output:
                command_handover = False
                print(output)
    finally:
        del bash_interface

# %%
