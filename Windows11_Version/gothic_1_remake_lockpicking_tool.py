#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

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
        self.style.configure("Green.TCombobox", foreground="#2e7d32")
        self.style.configure("Red.TCombobox", foreground="#c62828")
        
        self.style.map('Treeview', background=[('selected', '#4a7c59')])
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_frame = ttk.Frame(main_frame)
        self.setup_frame.pack(fill=tk.X)
        
        # --- Starting Positions ---
        top_setup = ttk.Frame(self.setup_frame)
        top_setup.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_setup, text="Number of Plates:").pack(side=tk.LEFT, padx=(0, 5))
        self.num_plates_var = tk.StringVar(value="5")
        self.num_plates_cb = ttk.Combobox(top_setup, textvariable=self.num_plates_var, values=[str(x) for x in range(3, 11)], state="readonly", width=5)
        self.num_plates_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.num_plates_cb.bind("<<ComboboxSelected>>", self.update_num_plates)
        
        self.start_vars = []
        self.start_labels = []
        self.start_spins = []
        
        start_container = ttk.Frame(top_setup)
        start_container.pack(side=tk.LEFT)
        
        for i in range(10):
            lbl = ttk.Label(start_container, text=f"Piston {i+1}:")
            lbl.grid(row=0, column=i*2, padx=(5,2))
            var = tk.IntVar(value=4)
            spin = ttk.Spinbox(start_container, from_=1, to=7, textvariable=var, width=3, state="readonly")
            spin.grid(row=0, column=i*2+1, padx=(0,5))
            
            # Remove highlight on click
            spin.bind("<FocusIn>", lambda e: self.root.focus_set())
            
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
                cb = ttk.Combobox(self.behaviors_frame, textvariable=var, values=options, width=8, state="readonly")
                cb.grid(row=i+1, column=j+1, padx=3, pady=3)
                
                if i == j:
                    cb.configure(style="Green.TCombobox")
                    cb.bind("<Button-1>", lambda e: "break")
                    cb.bind("<Key>", lambda e: "break")
                else:
                    cb.bind("<<ComboboxSelected>>", self.on_combobox_select)
                    
                cb.bind("<FocusIn>", lambda e: self.root.focus_set())
                
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
        
        self.tree.tag_configure("bookmark", background="#4a7c59", foreground="white")
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        
        self.root.bind("<Button-1>", lambda e: self.root.focus_set())
        
    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        tags = self.tree.item(item, "tags")
        if tags and "bookmark" in tags:
            new_tags = tuple(t for t in tags if t != "bookmark")
            self.tree.item(item, tags=new_tags)
        else:
            new_tags = tags + ("bookmark",) if tags else ("bookmark",)
            self.tree.item(item, tags=new_tags)
            
        self.tree.selection_remove(self.tree.selection())
        
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

    def toggle_setup(self):
        if self.is_setup_hidden:
            self.setup_frame.pack(fill=tk.X, before=self.btn_frame)
            self.toggle_setup_btn.config(text="Hide Setup")
            self.is_setup_hidden = False
        else:
            self.setup_frame.pack_forget()
            self.toggle_setup_btn.config(text="Show Setup")
            self.is_setup_hidden = True

    def on_combobox_select(self, event):
        cb = event.widget
        val = cb.get()
        if val == "Same":
            cb.configure(style="Green.TCombobox")
        elif val == "Opposite":
            cb.configure(style="Red.TCombobox")
        else:
            cb.configure(style="")

    def reset_defaults(self):
        self.root.geometry("800x600")
        if self.is_setup_hidden:
            self.toggle_setup()
            
        self.num_plates_var.set("5")
        self.update_num_plates()
        
        self.tree.delete(*self.tree.get_children())
        
        for i in range(10):
            self.start_vars[i].set(4)
            for j in range(10):
                if i == j:
                    self.behavior_vars[i][j].set("Same")
                    self.behavior_cbs[i][j].configure(style="Green.TCombobox")
                else:
                    self.behavior_vars[i][j].set("None")
                    self.behavior_cbs[i][j].configure(style="")

    def load_default_example(self):
        self.num_plates_var.set("6")
        self.update_num_plates()
        
        default_start = [6, 1, 1, 6, 1, 4]
        for i, val in enumerate(default_start):
            self.start_vars[i].set(val)
            
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
                    self.behavior_cbs[i][j].configure(style="Green.TCombobox")
                else:
                    self.behavior_vars[i][j].set("None")
                    self.behavior_cbs[i][j].configure(style="")
                    
        for i in range(6):
            for j in range(6):
                val = default_behaviors[i][j]
                self.behavior_vars[i][j].set(val)
                cb = self.behavior_cbs[i][j]
                if val == "Same":
                    cb.configure(style="Green.TCombobox")
                elif val == "Opposite":
                    cb.configure(style="Red.TCombobox")
                else:
                    cb.configure(style="")

    def solve_puzzle(self):
        self.tree.delete(*self.tree.get_children())
        
        try:
            start_state = [self.start_vars[i].get() for i in range(self.num_plates)]
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
                item = self.tree.insert("", tk.END, values=(str(current_step), move_desc, state_str))
                
                for k in range(current_step, current_step + num_moves):
                    if k % 10 == 0:
                        self.tree.item(item, tags=("bookmark",))
                        break
                        
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
    import sv_ttk
    root = tk.Tk()
    
    # Apply Windows 11 Sun Valley dark theme
    sv_ttk.set_theme("dark")
    
    app = LockpickingSolverWin11(root)
    root.mainloop()
