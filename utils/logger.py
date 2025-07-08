import os
import datetime

log_file = None

def init_log(log_dir):
    global log_file
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"injection_log_{timestamp}.txt")
    log_file = open(log_path, "w", encoding="utf-8")
    log(f"=== Territory Injector Log Started: {timestamp} ===\n")

def log(message):
    print(message)  # Optional: comment this out if you want silent runs
    if log_file:
        log_file.write(message + "\n")
