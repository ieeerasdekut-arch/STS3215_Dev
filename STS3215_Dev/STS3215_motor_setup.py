import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import requests

# Import the existing functions from your driver file
from sts3215_driver import move_angle, set_torque, set_mode, set_multiturn, get_status, ESP_IP

# --- EXTENDED API FUNCTIONS ---
def assign_motor_id(old_id, new_id):
    try:
        url = f"{ESP_IP}/set_id?id={old_id}&new_id={new_id}"
        resp = requests.get(url, timeout=1.0)
        if resp.status_code == 200:
            return True, f"Successfully changed ID {old_id} to {new_id}"
        else:
            return False, f"Failed with status: {resp.status_code}"
    except Exception as e:
        return False, f"Connection issue: {e}"

# --- GUI CLASS ---

class MotorSetupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("STS3215 Motor Setup & Diagnostic Tool")
        self.root.geometry("680x580")
        self.root.resizable(False, False)

        # Thread-safe queue for GUI updates
        self.gui_queue = queue.Queue()
        
        # Live tracking variables
        self.live_monitoring = False
        self.tracked_ids = set() # Keeps track of which motors to poll

        self._build_ui()
        
        # Start checking the queue for thread messages
        self.root.after(100, self.process_queue)

    def _build_ui(self):
        # Top label
        tk.Label(self.root, text="STS Motor Diagnostics & Configuration", font=("Arial", 14, "bold")).pack(pady=10)

        # Main layout frame
        content = tk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=10)

        # --- LEFT PANEL: Diagnostics ---
        left_panel = tk.LabelFrame(content, text="Motor Status & Discovery", padx=10, pady=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Data Treeview (Table)
        columns = ("ID", "Pos", "Volt (V)", "Temp (C)", "Load")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=65, anchor="center")
        self.tree.pack(fill="x", pady=5)

        # Scan Buttons
        btn_frame = tk.Frame(left_panel)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="Scan All (0-10)", bg="#d3e0dc", command=self.scan_all).pack(side="left", fill="x", expand=True, padx=2)
        
        self.entry_ping = tk.Entry(btn_frame, width=5)
        self.entry_ping.insert(0, "0")
        self.entry_ping.pack(side="left", padx=2)
        tk.Button(btn_frame, text="Ping ID", bg="#e6e6fa", command=self.ping_single).pack(side="left", fill="x", expand=True, padx=2)

        # Live Monitor Toggle
        self.btn_live = tk.Button(left_panel, text="Start Live Monitor (OFF)", bg="#FFB6C1", font=("Arial", 10, "bold"), command=self.toggle_live)
        self.btn_live.pack(fill="x", pady=(10, 0))


        # --- RIGHT PANEL: Control & Setup ---
        right_panel = tk.Frame(content)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 1. Target ID Frame
        id_frame = tk.LabelFrame(right_panel, text="Target Motor ID", font=("Arial", 10, "bold"), padx=10, pady=5, bg="#FFFACD")
        id_frame.pack(fill="x", pady=(0, 10))
        self.entry_target_id = tk.Entry(id_frame, font=("Arial", 12), width=10, justify="center")
        self.entry_target_id.insert(0, "0")
        self.entry_target_id.pack(pady=5)

        # 2. Movement & Torque Control
        ctrl_frame = tk.LabelFrame(right_panel, text="Basic Control", padx=10, pady=10)
        ctrl_frame.pack(fill="x", pady=5)

        t_btn_frame = tk.Frame(ctrl_frame)
        t_btn_frame.pack(fill="x", pady=2)
        tk.Button(t_btn_frame, text="Enable Torque", bg="#c6e2ff", command=lambda: self.run_thread(self._set_torque_thread, True)).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(t_btn_frame, text="Disable Torque", bg="#f8d5d5", command=lambda: self.run_thread(self._set_torque_thread, False)).pack(side="left", expand=True, fill="x", padx=2)

        move_inputs = tk.Frame(ctrl_frame)
        move_inputs.pack(fill="x", pady=(10, 2))
        tk.Label(move_inputs, text="Angle (-180 to 180):").grid(row=0, column=0, padx=2)
        self.entry_angle = tk.Entry(move_inputs, width=8)
        self.entry_angle.insert(0, "90")
        self.entry_angle.grid(row=0, column=1, padx=2)

        tk.Label(move_inputs, text="Speed:").grid(row=0, column=2, padx=2)
        self.entry_speed = tk.Entry(move_inputs, width=8)
        self.entry_speed.insert(0, "800")
        self.entry_speed.grid(row=0, column=3, padx=2)

        tk.Button(ctrl_frame, text="Move (Angle Type)", bg="#90EE90", command=self.move_motor).pack(fill="x", pady=5)

        # 3. Advanced Settings
        adv_frame = tk.LabelFrame(right_panel, text="Advanced Configuration", padx=10, pady=10)
        adv_frame.pack(fill="x", pady=5)

        # Assign ID
        id_set_frame = tk.Frame(adv_frame)
        id_set_frame.pack(fill="x", pady=2)
        tk.Label(id_set_frame, text="New ID:").pack(side="left")
        self.entry_new_id = tk.Entry(id_set_frame, width=5)
        self.entry_new_id.pack(side="left", padx=5)
        tk.Button(id_set_frame, text="Set ID", command=self.set_new_id).pack(side="right")

        # Mode
        mode_frame = tk.Frame(adv_frame)
        mode_frame.pack(fill="x", pady=2)
        tk.Label(mode_frame, text="Mode (0=Pos, 3=Spin):").pack(side="left")
        self.entry_mode = tk.Entry(mode_frame, width=5)
        self.entry_mode.insert(0, "0")
        self.entry_mode.pack(side="left", padx=5)
        tk.Button(mode_frame, text="Set Mode", command=self.set_mode_btn).pack(side="right")

        # Multiturn
        mt_frame = tk.Frame(adv_frame)
        mt_frame.pack(fill="x", pady=2)
        tk.Button(mt_frame, text="Enable Multiturn", command=lambda: self.run_thread(self._multiturn_thread, True)).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(mt_frame, text="Disable Multiturn", command=lambda: self.run_thread(self._multiturn_thread, False)).pack(side="left", expand=True, fill="x", padx=2)

        # Status Bar
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="blue", font=("Arial", 10))
        self.status_label.pack(side="bottom", pady=5, fill="x")


    # --- QUEUE PROCESSOR (Safely updates GUI) ---
    def process_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_label.config(text=f"Status: {data}")
                
                elif msg_type == "clear_tree":
                    for item in self.tree.get_children():
                        self.tree.delete(item)
                
                elif msg_type == "update_tree":
                    # Update row if exists, else create new row
                    m_id = str(data["id"])
                    vals = (data["id"], data["pos"], data["volt"], data["temp"], data["load"])
                    
                    if self.tree.exists(m_id):
                        self.tree.item(m_id, values=vals)
                    else:
                        self.tree.insert("", "end", iid=m_id, values=vals)
                
                elif msg_type == "error":
                    self.status_label.config(text=f"Error: {data}", fg="red")
                
                elif msg_type == "success":
                    self.status_label.config(text=f"Success: {data}", fg="green")
                    
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue) # Run again in 100ms

    def run_thread(self, target_func, *args):
        """Helper to start threads quickly"""
        threading.Thread(target=target_func, args=args, daemon=True).start()


    # --- LIVE MONITORING ---
    
    def toggle_live(self):
        if not self.live_monitoring:
            if not self.tracked_ids:
                messagebox.showinfo("Notice", "Please 'Scan' or 'Ping' at least one motor first so the monitor knows what to track.")
                return
                
            self.live_monitoring = True
            self.btn_live.config(text="Stop Live Monitor (ON)", bg="#90EE90")
            self.gui_queue.put(("status", "Live monitoring started..."))
            self.run_thread(self._live_monitor_thread)
        else:
            self.live_monitoring = False
            self.btn_live.config(text="Start Live Monitor (OFF)", bg="#FFB6C1")
            self.gui_queue.put(("status", "Live monitoring stopped."))

    def _live_monitor_thread(self):
        while self.live_monitoring:
            # Safely copy the set so it doesn't change size while looping
            current_ids = list(self.tracked_ids)
            
            for m_id in current_ids:
                if not self.live_monitoring: 
                    break
                
                data = get_status(m_id)
                if data:
                    self.gui_queue.put(("update_tree", {
                        "id": m_id,
                        "pos": data.get('pos', 'ERR'),
                        "volt": data.get('volt', 'ERR'),
                        "temp": data.get('temp', 'ERR'),
                        "load": data.get('load', 'ERR')
                    }))
            
            # Brief pause to not crash ESP32 web server with requests
            time.sleep(0.1)


    # --- ACTION METHODS (These run in background threads) ---

    def scan_all(self):
        self.gui_queue.put(("status", "Scanning IDs 0 to 10..."))
        self.gui_queue.put(("clear_tree", ""))
        self.tracked_ids.clear() # Reset tracked IDs
        self.run_thread(self._scan_thread, range(11))

    def ping_single(self):
        try:
            target = int(self.entry_ping.get())
            self.gui_queue.put(("status", f"Pinging ID {target}..."))
            self.run_thread(self._scan_thread, [target])
        except ValueError:
            self.gui_queue.put(("error", "Invalid ID for ping"))

    def _scan_thread(self, id_list):
        found = 0
        for i in id_list:
            if self.live_monitoring:
                break # Cancel manual scan if live monitor is active
                
            self.gui_queue.put(("status", f"Checking ID {i}..."))
            data = get_status(i)
            if data:
                found += 1
                self.tracked_ids.add(i) # Add to tracked set
                self.gui_queue.put(("update_tree", {
                    "id": i,
                    "pos": data.get('pos', 'N/A'),
                    "volt": data.get('volt', 'N/A'),
                    "temp": data.get('temp', 'N/A'),
                    "load": data.get('load', 'N/A')
                }))
        
        if found > 0:
            self.gui_queue.put(("success", f"Scan complete. Found {found} motor(s)."))
        else:
            self.gui_queue.put(("error", "Scan complete. No motors found. Check connections/power."))


    def _set_torque_thread(self, enable):
        try:
            m_id = int(self.entry_target_id.get())
            self.gui_queue.put(("status", f"Setting Torque for ID {m_id}..."))
            set_torque(m_id, enable)
            state = "Enabled" if enable else "Disabled"
            self.gui_queue.put(("success", f"Torque {state} on ID {m_id}"))
        except ValueError:
            self.gui_queue.put(("error", "Invalid Target ID"))
        except Exception as e:
            self.gui_queue.put(("error", str(e)))

    def move_motor(self):
        try:
            m_id = int(self.entry_target_id.get())
            angle = float(self.entry_angle.get())
            spd = int(self.entry_speed.get())
            
            raw_pos = int((4095 * angle) / 360)
            self.gui_queue.put(("status", f"Moving ID {m_id} to {angle}° (Pos: {raw_pos})..."))
            self.run_thread(self._move_thread, m_id, angle, spd)
        except ValueError:
            self.gui_queue.put(("error", "Invalid Move Inputs"))

    def _move_thread(self, m_id, angle, spd):
        try:
            move_angle(m_id, angle, speed=spd)
            self.gui_queue.put(("success", f"Move command sent to ID {m_id}"))
        except Exception as e:
            self.gui_queue.put(("error", str(e)))

    def set_new_id(self):
        try:
            old_id = int(self.entry_target_id.get())
            new_id = int(self.entry_new_id.get())
            self.gui_queue.put(("status", f"Changing ID {old_id} to {new_id}..."))
            self.run_thread(self._set_id_thread, old_id, new_id)
        except ValueError:
            self.gui_queue.put(("error", "Invalid IDs provided"))

    def _set_id_thread(self, old_id, new_id):
        success, msg = assign_motor_id(old_id, new_id)
        if success:
            self.gui_queue.put(("success", msg))
        else:
            self.gui_queue.put(("error", msg))

    def set_mode_btn(self):
        try:
            m_id = int(self.entry_target_id.get())
            mode = int(self.entry_mode.get())
            self.gui_queue.put(("status", f"Setting mode {mode} for ID {m_id}..."))
            self.run_thread(self._set_mode_thread, m_id, mode)
        except ValueError:
            self.gui_queue.put(("error", "Invalid Mode or ID"))

    def _set_mode_thread(self, m_id, mode):
        try:
            set_mode(m_id, mode)
            self.gui_queue.put(("success", f"Mode {mode} set for ID {m_id}"))
        except Exception as e:
            self.gui_queue.put(("error", str(e)))

    def _multiturn_thread(self, enable):
        try:
            m_id = int(self.entry_target_id.get())
            self.gui_queue.put(("status", f"Setting Multiturn for ID {m_id}..."))
            set_multiturn(m_id, enable)
            state = "Enabled" if enable else "Disabled"
            self.gui_queue.put(("success", f"Multiturn {state} on ID {m_id}"))
        except ValueError:
            self.gui_queue.put(("error", "Invalid Target ID"))
        except Exception as e:
            self.gui_queue.put(("error", str(e)))


if __name__ == "__main__":
    root = tk.Tk()
    app = MotorSetupGUI(root)
    root.mainloop()