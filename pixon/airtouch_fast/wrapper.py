import socket
import time
import threading
import random
import string
import os
import subprocess
from .utils import run_adb_command, get_abi, get_display_info, push_file, chmod

class MinitouchWrapper:
    def __init__(self, serial=None, bin_path=None):
        self.serial = serial
        self.bin_path = bin_path or os.path.join(os.path.dirname(__file__), "binaries")
        self.socket_name = f"minitouch_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
        self.host_port = None
        self.sock = None
        
        # Device constraints from header
        self.version = None
        self.max_contacts = None
        self.max_x = None
        self.max_y = None
        self.max_pressure = None
        self.pid = None
        
        # Display resolution
        self.display_w, self.display_h = get_display_info(self.serial)
        
        self._running = False
        self._lock = threading.Lock()

    def _get_local_binary(self):
        abi = get_abi(self.serial)
        # Map common ABIs to minitouch binary folders
        abi_map = {
            "arm64-v8a": "arm64-v8a",
            "armeabi-v7a": "armeabi-v7a",
            "armeabi": "armeabi-v7a",
            "x86": "x86",
            "x86_64": "x86_64"
        }
        target_abi = abi_map.get(abi)
        if not target_abi:
            raise RuntimeError(f"Unsupported ABI: {abi}")
        
        local_bin = os.path.join(self.bin_path, target_abi, "minitouch")
        if not os.path.exists(local_bin):
            # Fallback for some emulators that might report x86 but can run others, 
            # or if the user hasn't downloaded binaries yet.
            raise FileNotFoundError(f"Minitouch binary not found at {local_bin}. Please run the download script.")
        return local_bin

    def _push_and_start_daemon(self):
        remote_path = "/data/local/tmp/minitouch"
        local_bin = self._get_local_binary()
        
        push_file(local_bin, remote_path, self.serial)
        chmod(remote_path, "755", self.serial)
        
        # Start daemon in background
        # -n specifies the abstract socket name
        cmd = f"adb {'-s ' + self.serial if self.serial else ''} shell {remote_path} -n {self.socket_name}"
        self.daemon_proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for daemon to initialize abstract socket
        time.sleep(1.0)

    def start(self, retries=5, delay=1):
        with self._lock:
            if self._running:
                return
            
            self._push_and_start_daemon()
            
            # ADB Forward
            # We use tcp:0 to let ADB pick an available port
            forward_out = run_adb_command(f"forward tcp:0 localabstract:{self.socket_name}", self.serial)
            self.host_port = int(forward_out)
            
            # Connect Socket with retries
            for attempt in range(retries):
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(2.0)
                    self.sock.connect(("127.0.0.1", self.host_port))
                    self._parse_header()
                    self._running = True
                    print(f"Minitouch started on port {self.host_port}. Constraints: {self.max_x}x{self.max_y}")
                    return
                except (socket.error, socket.timeout) as e:
                    if attempt == retries - 1:
                        self.stop()
                        raise RuntimeError(f"Failed to connect to minitouch socket after {retries} attempts: {e}")
                    time.sleep(delay)

    def _parse_header(self):
        """Reads and parses the minitouch header."""
        # Header format:
        # v <version>
        # ^ <max-contacts> <max-x> <max-y> <max-pressure>
        # $ <pid>
        data = self.sock.recv(1024).decode('utf-8')
        lines = data.strip().split('\n')
        for line in lines:
            parts = line.split()
            if not parts: continue
            if parts[0] == 'v':
                self.version = int(parts[1])
            elif parts[0] == '^':
                self.max_contacts = int(parts[1])
                self.max_x = int(parts[2])
                self.max_y = int(parts[3])
                self.max_pressure = int(parts[4])
            elif parts[0] == '$':
                self.pid = int(parts[1])

    def stop(self):
        with self._lock:
            if not self._running:
                return
            
            if self.sock:
                self.sock.close()
            
            run_adb_command(f"forward --remove tcp:{self.host_port}", self.serial)
            
            # Kill the process on device
            if self.pid:
                run_adb_command(f"shell kill {self.pid}", self.serial)
            
            self._running = False

    def _map_coords(self, x, y):
        """Maps display coordinates to minitouch coordinate space."""
        # If display size is unknown, return as is (assuming normalized or already mapped)
        if not self.display_w or not self.max_x:
            return int(x), int(y)
        
        new_x = int(x * self.max_x / self.display_w)
        new_y = int(y * self.max_y / self.display_h)
        return new_x, new_y

    def _send(self, msg):
        if not self._running:
            raise RuntimeError("Minitouch not running")
        self.sock.send(f"{msg}\n".encode('utf-8'))

    def touch(self, x, y, pressure=50, duration=None):
        mx, my = self._map_coords(x, y)
        self._send(f"d 0 {mx} {my} {pressure}")
        self._send("c")
        
        if duration:
            time.sleep(duration)
        
        self._send("u 0")
        self._send("c")

    def swipe(self, start_pt, end_pt, duration=0.5, steps=20, pressure=50):
        x1, y1 = start_pt
        x2, y2 = end_pt
        
        mx1, my1 = self._map_coords(x1, y1)
        mx2, my2 = self._map_coords(x2, y2)
        
        self._send(f"d 0 {mx1} {my1} {pressure}")
        self._send("c")
        
        interval = duration / steps
        for i in range(1, steps + 1):
            curr_x = mx1 + (mx2 - mx1) * i / steps
            curr_y = my1 + (my2 - my1) * i / steps
            self._send(f"m 0 {int(curr_x)} {int(curr_y)} {pressure}")
            self._send("c")
            time.sleep(interval)
            
        self._send("u 0")
        self._send("c")

    def pinch(self, center, radius_start, radius_end, duration=0.5, steps=20):
        """Performs a two-finger pinch or zoom."""
        cx, cy = center
        
        interval = duration / steps
        
        # Initial points
        p1_start = (cx - radius_start, cy)
        p2_start = (cx + radius_start, cy)
        
        mx1_s, my1_s = self._map_coords(*p1_start)
        mx2_s, my2_s = self._map_coords(*p2_start)
        
        # Touch down both fingers
        self._send(f"d 0 {mx1_s} {my1_s} 50")
        self._send(f"d 1 {mx2_s} {my2_s} 50")
        self._send("c")
        
        for i in range(1, steps + 1):
            curr_radius = radius_start + (radius_end - radius_start) * i / steps
            
            p1_curr = (cx - curr_radius, cy)
            p2_curr = (cx + curr_radius, cy)
            
            mx1_c, my1_c = self._map_coords(*p1_curr)
            mx2_c, my2_c = self._map_coords(*p2_curr)
            
            self._send(f"m 0 {mx1_c} {my1_c} 50")
            self._send(f"m 1 {mx2_c} {my2_c} 50")
            self._send("c")
            time.sleep(interval)
            
        self._send("u 0")
        self._send("u 1")
        self._send("c")

    def reset(self):
        self._send("r")
        self._send("c")
