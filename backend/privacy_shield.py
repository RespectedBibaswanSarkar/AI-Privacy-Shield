import multiprocessing
import tkinter as tk
import time

def _run_shield(queue):
    """
    Internal function to run the Tkinter GUI in a separate process.
    """
    root = tk.Tk()
    root.title("Synapse Privacy Shield")
    
    # Configure window to be fullscreen, black, and on top
    root.configure(bg='black')
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    # Start hidden
    root.withdraw()
    
    # Label for the blackout screen
    label = tk.Label(root, text="⚠️ ACCESS DENIED ⚠️\nUNAUTHORIZED VIEWER DETECTED", 
                     font=("Courier New", 40, "bold"), fg="red", bg="black")
    label.pack(expand=True)
    
    def check_queue():
        try:
            while not queue.empty():
                msg = queue.get_nowait()
                if msg == "SHOW":
                    root.deiconify()
                    root.attributes('-topmost', True) # Enforce on top again
                elif msg == "HIDE":
                    root.withdraw()
                elif msg == "EXIT":
                    root.destroy()
                    return
        except Exception:
            pass
        # Check again in 100ms
        root.after(100, check_queue)
        
    root.after(100, check_queue)
    root.mainloop()

class PrivacyShield:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.process = None
        self.active = False
        
    def start(self):
        if self.process is None or not self.process.is_alive():
            self.process = multiprocessing.Process(target=_run_shield, args=(self.queue,), daemon=True)
            self.process.start()
            
    def activate(self):
        if not self.active:
            self.queue.put("SHOW")
            self.active = True
            
    def deactivate(self):
        if self.active:
            self.queue.put("HIDE")
            self.active = False
            
    def stop(self):
        self.queue.put("EXIT")
        if self.process:
            self.process.join(timeout=1)
            self.process = None
