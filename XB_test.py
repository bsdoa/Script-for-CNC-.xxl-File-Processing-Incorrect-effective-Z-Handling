import time
import os
import re
import shutil
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# Ορισμός τίτλου παραθύρου
os.system("title XB mono")

# -----------------------------
# A. Ορισμοί regex για τις τριάδες γραμμών
# -----------------------------
pattern_exclude_3digit_T = re.compile(r'^.*\bT=\d{3}\b.*$')
pattern_line1 = re.compile(r'^XG0\s+Z=-2\.000\s+T=(\d{1,2})\s*$')
pattern_line2 = re.compile(r'^XL2P\s+Z=([-\d.]+)\s+T=(\d{1,2})\s+V\d{7}\s*$')
pattern_line3 = re.compile(r'^XG0\s+Z=-1\.000\s+T=(\d{1,2})\s*$')

# -----------------------------
# B. Ορισμοί regex για μετατροπή γραμμών XG0 σε XB
# -----------------------------
pattern_xg0 = re.compile(
    r'^XG0(?:\s+X=([-\d.]+))?(?:\s+Y=([-\d.]+))?(?:\s+Z=([-\d.]+))?(?:\s+T=(\d{1,2}))?(.*)?$'
)

# -----------------------------
# C. Βοηθητικές συναρτήσεις
# -----------------------------
def find_triple_sequences(lines):
    triple_sequences = []
    i = 0
    while i <= len(lines) - 3:
        l1, l2, l3 = lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()
        if pattern_line1.match(l1) and pattern_line3.match(l3):
            m = pattern_line2.match(l2)
            if m:
                triple_sequences.append((i, i+2, m.group(1)))
                i += 3
                continue
        i += 1
    return triple_sequences

def effective_z_for_index(i, triple_sequences):
    candidate = None
    for (start, end, z) in triple_sequences:
        if end <= i:
            candidate = z
        elif start > i:
            if candidate is None:
                candidate = z
            break
    return candidate

def transform_XG0_line_with_effective_z(line, effective_z):
    m = pattern_xg0.match(line.strip())
    if m:
        x, y, z, t, extra = m.groups()
        if not t:
            return line  # Αν δεν υπάρχει T, επιστρέφουμε τη γραμμή όπως είναι
        return f"XB{' X='+x if x else ''}{' Y='+y if y else ''} Z={effective_z} T={t} V1800 G=0{extra or ''}\n"
    return line

# -----------------------------
# D. Διαχείριση αρχείων
# -----------------------------
class FileHandler(FileSystemEventHandler):
    def __init__(self):
        self.processing_files = set()
        super().__init__()

    def on_created(self, event):
        if event.src_path.endswith((".XXL", ".xxl")):
            print(f"New file detected: {event.src_path}")
            threading.Thread(target=self.handle_file, args=(event.src_path,)).start()

    def on_modified(self, event):
        if event.src_path.endswith((".XXL", ".xxl")):
            print(f"Modified file detected")
            threading.Thread(target=self.handle_file, args=(event.src_path,)).start()

    def handle_file(self, file_path):
        time.sleep(1)
        if file_path in self.processing_files:
            print(f"[DEBUG] Skipping already processing file: {file_path}")
            return
        self.processing_files.add(file_path)
        try:
            wait_for_file_availability(file_path)
            if not self.is_already_processed(file_path):
                process_file(file_path)
                self.create_new_script_and_restart()
            else:
                print(f"File already processed or manually modified, ignoring: {file_path}")
        finally:
            self.processing_files.remove(file_path)

    def is_already_processed(self, file_path):
        try:
            with open(file_path, "r") as file:
                if any(line.strip() == "XN X=P0" for line in file):
                    return True
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        return False

    def create_new_script_and_restart(self):
        current_script_path = os.path.realpath(__file__)
        new_script_path = current_script_path.replace("_new.py", ".py") if current_script_path.endswith("_new.py") else current_script_path.replace(".py", "_new.py")
        shutil.copy(current_script_path, new_script_path)
        print(f"New script created: {new_script_path}")
        print(f"[DEBUG] Restarting to run: {new_script_path}")
        os.execv(sys.executable, [sys.executable, new_script_path])

def wait_for_file_availability(file_path):
    while True:
        try:
            with open(file_path, 'r+'):
                return
        except (PermissionError, FileNotFoundError):
            print(f"[DEBUG] Waiting for file to be available: {file_path}")
            time.sleep(0.5)

def process_file(file_path):
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except Exception as e:
        print(f"[ERROR] Unable to read file {file_path}: {e}")
        return

    triple_sequences = find_triple_sequences(lines)
    new_lines = []
    i = 0
    while i < len(lines):
        triple_found = any(start == i for start, _, _ in triple_sequences)

        # Έλεγχος γα τη γραμμή πριν την τριάδα
        if i > 0 and any(start == i - 1 for start, _, _ in triple_sequences):
            effective_z = effective_z_for_index(i - 1, triple_sequences)
            new_lines.append(transform_XG0_line_with_effective_z(lines[i - 1], effective_z) if effective_z else lines[i - 1])

        if triple_found:
            new_lines.append(";\n")
            i += 3
            continue

        if pattern_exclude_3digit_T.match(lines[i].strip()):
            new_lines.append(lines[i])  # Αν η γραμμή έχει T=xxx, την αφήνουμε ως έχει
        elif lines[i].lstrip().startswith("XG0"):
            effective_z = effective_z_for_index(i, triple_sequences)
            new_lines.append(transform_XG0_line_with_effective_z(lines[i], effective_z) if effective_z else lines[i])
        else:
            new_lines.append(lines[i])
        i += 1

    with open(file_path, "w") as file:
        file.writelines(new_lines)
    print(f"XXL file saved and updated: {file_path}")

# -----------------------------
# E. Εκκίνηση παρακολούθησης φακέλων
# -----------------------------
if __name__ == "__main__":
    paths = [
        r"destination"
    ]
    event_handler = FileHandler()
    observer = Observer()
    for path in paths:
        observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        print("[DEBUG] Monitoring for changes in the folders.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
