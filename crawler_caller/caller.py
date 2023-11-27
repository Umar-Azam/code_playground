
# %%
import subprocess


# %%

def generate_config(url : str, match : str, num_pages : int) :
    return (f'''import {{ Config }} from "./src/config";

export const defaultConfig: Config = {{
  url: "{url}",
  match: "{match}",
  maxPagesToCrawl: {num_pages},
  outputFileName: "../data/output.json",
}};''')

# Example url : https://www.builder.io/c/docs/developers
# Example match : https://www.builder.io/c/docs/**

with open('./crawler/data/testconfig.ts','w') as file:
    file.write(generate_config('123','345',10))

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
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()

    def read_output(self):
        try:
            output = []
            while (self.output_queue.qsize() != 0):
                output.append(self.output_queue.get())
            return output
        except queue.Empty:
            return None

    def _io_loop(self):
        while self.running:
            output = self.process.stdout.readline()
            if output:
                self.output_queue.put(output)
            else:
                break


# %%
if __name__ == "__main__":
    bash_interface = BashInterface()

    try:
        
        while True:
            bash_interface.write_command(input("Input CMD :"))

            time.sleep(0.1)

            output = bash_interface.read_output()
            if output:
                print(output)
    finally:
        del bash_interface

# %%

# %%
