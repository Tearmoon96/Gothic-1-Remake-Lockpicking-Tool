#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import sv_ttk

def solve_bfs(start_state, behaviors):
    target_state = tuple([4] * len(start_state))
    start_tuple = tuple(start_state)
    
    queue = deque([(start_tuple, [])])
    visited = set([start_tuple])
    
    while queue:
        current_state, path = queue.popleft()
        
        if current_state == target_state:
            return path
            
        for p in range(len(start_state)):
            for d, d_name in [(1, "Left"), (-1, "Right")]:
                valid = True
                next_state = list(current_state)
                
                for affected_idx in range(len(start_state)):
                    effect = behaviors[p][affected_idx]
                    if effect != 0:
                        change = d * effect
                        next_state[affected_idx] += change
                        
                        if next_state[affected_idx] < 1 or next_state[affected_idx] > 7:
                            valid = False
                            break
                            
                if valid:
                    next_tuple = tuple(next_state)
                    if next_tuple not in visited:
                        visited.add(next_tuple)
                        state_str = ", ".join(map(str, next_tuple))
                        move_desc = f"Plate {p+1} {d_name}"
                        new_path = path + [(move_desc, state_str)]
                        queue.append((next_tuple, new_path))
                        
    return None

class LockpickingSolverWin11:
    def __init__(self, root):
        self.root = root
        self.root.title("Gothic 1 Remake Lockpicking Tool")
        self.root.geometry("800x600")
        
        self.num_plates = 5

        self.style = ttk.Style()
        self.style.configure("Fixed.TEntry", fieldbackground="#e8e8e8",
                             foreground="#4a7c59", font=("TkDefaultFont", 9, "bold"))

        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_frame = ttk.Frame(main_frame)
        self.setup_frame.pack(fill=tk.X)
        
        # --- Number of Plates ---
        plates_row = ttk.Frame(self.setup_frame)
        plates_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(plates_row, text="Number of Plates:").pack(side=tk.LEFT, padx=(0, 5))
        self.num_plates_var = tk.StringVar(value="5")
        self.num_plates_cb = ttk.Combobox(plates_row, textvariable=self.num_plates_var, values=[str(x) for x in range(3, 11)], state="readonly", width=5)
        self.num_plates_cb.pack(side=tk.LEFT)
        self.num_plates_cb.bind("<<ComboboxSelected>>", self.update_num_plates)

        # --- Starting Positions ---
        piston_row = ttk.Frame(self.setup_frame)
        piston_row.pack(fill=tk.X, pady=(0, 10))

        self.start_vars = []
        self.start_labels = []
        self.start_spins = []

        start_container = ttk.Frame(piston_row)
        start_container.pack(side=tk.LEFT)
        
        for i in range(10):
            lbl = ttk.Label(start_container, text=f"Piston {i+1}:")
            lbl.grid(row=0, column=i*2, padx=(5,2))
            var = tk.StringVar(value="4")
            spin = ttk.Combobox(start_container, textvariable=var, values=[str(x) for x in range(1, 8)], width=2, state="readonly")
            spin.grid(row=0, column=i*2+1, padx=(0,5))

            self.start_labels.append(lbl)
            self.start_spins.append(spin)
            self.start_vars.append(var)
            
            if i >= 5:
                lbl.grid_remove()
                spin.grid_remove()
                
        # --- Behaviors ---
        self.behaviors_frame = ttk.LabelFrame(self.setup_frame, text="Plate Behaviors", padding="10")
        self.behaviors_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.behaviors_frame, text="Moving... \\ Affects...").grid(row=0, column=0, padx=5, pady=5)
        self.behavior_col_labels = []
        self.behavior_row_labels = []
        self.behavior_vars = []
        self.behavior_cbs = []
        
        options = ["None", "Same", "Opposite"]
        for i in range(10):
            lbl_col = ttk.Label(self.behaviors_frame, text=f"Plate {i+1}")
            lbl_col.grid(row=0, column=i+1, padx=5, pady=5)
            self.behavior_col_labels.append(lbl_col)
            
            lbl_row = ttk.Label(self.behaviors_frame, text=f"Moving Plate {i+1}")
            lbl_row.grid(row=i+1, column=0, padx=5, pady=5, sticky=tk.W)
            self.behavior_row_labels.append(lbl_row)
            
            row_vars = []
            row_cbs = []
            for j in range(10):
                var = tk.StringVar(value="Same" if i == j else "None")
                if i == j:
                    cb = ttk.Entry(self.behaviors_frame, textvariable=var,
                                   style="Fixed.TEntry", state="readonly",
                                   justify="center", width=8)
                    cb.bind("<Button-1>", lambda e: "break")
                    cb.bind("<Key>", lambda e: "break")
                    cb.bind("<MouseWheel>", lambda e: "break")
                else:
                    cb = ttk.Combobox(self.behaviors_frame, textvariable=var, values=options, width=8, state="readonly")
                    cb.bind("<<ComboboxSelected>>", self.on_combobox_select)
                    cb.bind("<FocusIn>", self._defocus_cb)
                    self._force_cb_fg(cb, "#1a1a1a")
                cb.grid(row=i+1, column=j+1, padx=3, pady=3)
                
                row_vars.append(var)
                row_cbs.append(cb)
                
                if i >= 5 or j >= 5:
                    cb.grid_remove()
                    
            self.behavior_vars.append(row_vars)
            self.behavior_cbs.append(row_cbs)
            
            if i >= 5:
                lbl_col.grid_remove()
                lbl_row.grid_remove()
                
        # --- Buttons ---
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(self.btn_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(self.btn_frame, text="Load Default Example", command=self.load_default_example).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(self.btn_frame, text="Solve Puzzle", command=self.solve_puzzle).pack(side=tk.LEFT, padx=(0, 10))
        
        self.is_setup_hidden = False
        self.toggle_setup_btn = ttk.Button(self.btn_frame, text="Hide Setup", command=self.toggle_setup)
        self.toggle_setup_btn.pack(side=tk.LEFT)
        
        # --- Output ---
        output_frame = ttk.LabelFrame(main_frame, text="Solution Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(output_frame, columns=("Step", "Action", "State"), show="headings")
        self.tree.heading("Step", text="Step")
        self.tree.heading("Action", text="Action")
        self.tree.heading("State", text="State")
        
        self.tree.column("Step", width=50, anchor=tk.CENTER)
        self.tree.column("Action", width=250, anchor=tk.W)
        self.tree.column("State", width=150, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_num_plates(self, event=None):
        self.num_plates = int(self.num_plates_var.get())
        
        for i in range(10):
            visible = (i < self.num_plates)
            if visible:
                self.start_labels[i].grid()
                self.start_spins[i].grid()
                self.behavior_col_labels[i].grid()
                self.behavior_row_labels[i].grid()
            else:
                self.start_labels[i].grid_remove()
                self.start_spins[i].grid_remove()
                self.behavior_col_labels[i].grid_remove()
                self.behavior_row_labels[i].grid_remove()
                
            for j in range(10):
                if i < self.num_plates and j < self.num_plates:
                    self.behavior_cbs[i][j].grid()
                else:
                    self.behavior_cbs[i][j].grid_remove()

        self._refresh_all_cb_colors()

    def toggle_setup(self):
        if self.is_setup_hidden:
            self.setup_frame.pack(fill=tk.X, before=self.btn_frame)
            self.toggle_setup_btn.config(text="Hide Setup")
            self.is_setup_hidden = False
        else:
            self.setup_frame.pack_forget()
            self.toggle_setup_btn.config(text="Show Setup")
            self.is_setup_hidden = True

    def _defocus_cb(self, event):
        """Remove focus highlight from combobox after dropdown interaction."""
        self.root.after(10, self.root.focus_set)

    def on_combobox_select(self, event):
        cb = event.widget
        val = cb.get()
        if val == "Same":
            self._force_cb_fg(cb, "#4a7c59")
        elif val == "Opposite":
            self._force_cb_fg(cb, "#9e5c5c")
        else:
            self._force_cb_fg(cb, "#1a1a1a")
        self.root.after(5, self.root.focus_set)

    def _force_cb_fg(self, cb, color):
        """Force text color + bold on a themed Combobox by bypassing sv_ttk."""
        def _apply():
            try:
                cb.tk.call(cb._w, 'configure', '-foreground', color,
                           '-font', 'TkDefaultFont 9 bold')
            except Exception:
                pass
        cb.after(5, _apply)

    def _refresh_all_cb_colors(self):
        """Re-apply foreground colors to all visible behavior comboboxes."""
        for i in range(self.num_plates):
            for j in range(self.num_plates):
                if i == j:
                    continue  # diagonal cells are fixed Entry widgets
                val = self.behavior_vars[i][j].get()
                cb = self.behavior_cbs[i][j]
                if val == "Same":
                    self._force_cb_fg(cb, "#4a7c59")
                elif val == "Opposite":
                    self._force_cb_fg(cb, "#9e5c5c")
                else:
                    self._force_cb_fg(cb, "#1a1a1a")

    def reset_defaults(self):
        self.root.geometry("800x600")
        if self.is_setup_hidden:
            self.toggle_setup()
            
        self.num_plates_var.set("5")
        self.update_num_plates()
        
        self.tree.delete(*self.tree.get_children())
        
        for i in range(10):
            self.start_vars[i].set("4")
            for j in range(10):
                if i == j:
                    self.behavior_vars[i][j].set("Same")
                else:
                    self.behavior_vars[i][j].set("None")
                    self._force_cb_fg(self.behavior_cbs[i][j], "#1a1a1a")

    def load_default_example(self):
        self.num_plates_var.set("6")
        self.update_num_plates()
        
        default_start = [6, 1, 1, 6, 1, 4]
        for i, val in enumerate(default_start):
            self.start_vars[i].set(str(val))
            
        default_behaviors = [
            ["Same", "Same", "None", "Opposite", "None", "None"],
            ["None", "Same", "None", "Opposite", "Opposite", "None"],
            ["None", "None", "Same", "Same", "Opposite", "None"],
            ["None", "None", "Same", "Same", "None", "None"],
            ["None", "Same", "Opposite", "None", "Same", "None"],
            ["None", "None", "None", "None", "None", "Same"]
        ]
        
        for i in range(10):
            for j in range(10):
                if i == j:
                    self.behavior_vars[i][j].set("Same")
                else:
                    self.behavior_vars[i][j].set("None")
                    self._force_cb_fg(self.behavior_cbs[i][j], "#1a1a1a")
                    
        for i in range(6):
            for j in range(6):
                val = default_behaviors[i][j]
                self.behavior_vars[i][j].set(val)
                if i != j:
                    cb = self.behavior_cbs[i][j]
                    if val == "Same":
                        self._force_cb_fg(cb, "#4a7c59")
                    elif val == "Opposite":
                        self._force_cb_fg(cb, "#9e5c5c")
                    else:
                        self._force_cb_fg(cb, "#1a1a1a")

    def solve_puzzle(self):
        self.tree.delete(*self.tree.get_children())
        
        try:
            start_state = [int(self.start_vars[i].get()) for i in range(self.num_plates)]
            if any(val < 1 or val > 7 for val in start_state):
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showerror("Input Error", "Starting positions must be numbers between 1 and 7.")
            return
            
        behaviors = []
        for i in range(self.num_plates):
            row = []
            for j in range(self.num_plates):
                val = self.behavior_vars[i][j].get()
                if val == "Same":
                    row.append(1)
                elif val == "Opposite":
                    row.append(-1)
                else:
                    row.append(0)
            behaviors.append(row)
            
        path = solve_bfs(start_state, behaviors)
        
        if path is not None:
            compressed_path = []
            count = 1
            for i in range(len(path)):
                if i < len(path) - 1 and path[i][0] == path[i+1][0]:
                    count += 1
                else:
                    action = path[i][0]
                    if count > 1:
                        action += f" x{count}"
                    compressed_path.append((action, path[i][1], count))
                    count = 1
                    
            start_str = ", ".join(map(str, start_state))
            self.tree.insert("", tk.END, values=("-", "Start", start_str))
            
            current_step = 1
            for i, (move_desc, state_str, num_moves) in enumerate(compressed_path):
                self.tree.insert("", tk.END, values=(str(current_step), move_desc, state_str))

                current_step += num_moves
                
            if not self.is_setup_hidden:
                self.toggle_setup()
                
            items_to_fit = min(len(compressed_path) + 1, 15)
            target_height = 120 + (items_to_fit * 30)
            if self.root.winfo_height() < target_height:
                self.root.geometry(f"{self.root.winfo_width()}x{target_height}")
        else:
            self.tree.insert("", tk.END, values=("-", "No solution found for this configuration.", "-"))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Apply Windows 11 Sun Valley light theme
    sv_ttk.set_theme("light")
    
    app = LockpickingSolverWin11(root)
    root.mainloop()
