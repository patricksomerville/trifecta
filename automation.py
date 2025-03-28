
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Dict, List
import threading

class AutoSaver:
    def __init__(self, save_interval: int = 300):  # 5 minutes default
        self.save_interval = save_interval
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self.thread = None

    def register_callback(self, name: str, callback: Callable) -> None:
        self.callbacks[name] = callback

    def start(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self._auto_save_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join()

    def _auto_save_loop(self) -> None:
        while self.running:
            time.sleep(self.save_interval)
            for name, callback in self.callbacks.items():
                try:
                    callback()
                except Exception as e:
                    print(f"Error in auto-save callback {name}: {e}")

class FileWatcher:
    def __init__(self, directory: str, patterns: List[str]):
        self.directory = directory
        self.patterns = patterns
        self.callbacks: Dict[str, Callable] = {}
        self.observer = Observer()
        
    def register_callback(self, name: str, callback: Callable) -> None:
        self.callbacks[name] = callback

    def start(self) -> None:
        event_handler = self._create_event_handler()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join()

    def _create_event_handler(self) -> FileSystemEventHandler:
        class Handler(FileSystemEventHandler):
            def __init__(self, callbacks, patterns):
                self.callbacks = callbacks
                self.patterns = patterns

            def on_modified(self, event):
                if not event.is_directory:
                    if any(event.src_path.endswith(pat) for pat in self.patterns):
                        for name, callback in self.callbacks.items():
                            try:
                                callback(event.src_path)
                            except Exception as e:
                                print(f"Error in file watcher callback {name}: {e}")

        return Handler(self.callbacks, self.patterns)

class BatchProcessor:
    def __init__(self):
        self.tasks: Dict[str, Callable] = {}

    def register_task(self, name: str, task: Callable) -> None:
        self.tasks[name] = task

    def process_directory(self, directory: str, task_name: str) -> Dict[str, str]:
        if task_name not in self.tasks:
            raise ValueError(f"Task {task_name} not found")

        results = {}
        for root, _, files in os.walk(directory):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    result = self.tasks[task_name](filepath)
                    results[filepath] = result
                except Exception as e:
                    results[filepath] = f"Error: {str(e)}"

        return results
