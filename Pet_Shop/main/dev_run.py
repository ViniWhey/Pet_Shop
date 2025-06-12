# dev_run.py
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, run_cmd):
        self.run_cmd = run_cmd
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        # Caminho absoluto para main.py na mesma pasta que dev_run.py
        main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        self.process = subprocess.Popen([sys.executable, main_path])

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print("Arquivo alterado, reiniciando...")
            self.start_process()

if __name__ == "__main__":
    event_handler = RestartOnChangeHandler([sys.executable, "main.py"])
    observer = Observer()
    # Ajuste: monitora o diretório atual e subpastas
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    if event_handler.process:
        event_handler.process.terminate()