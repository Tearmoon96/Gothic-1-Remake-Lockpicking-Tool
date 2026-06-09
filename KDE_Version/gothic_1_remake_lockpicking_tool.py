#!/usr/bin/env python3
import sys
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QSpinBox, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QTabWidget, QAbstractItemView, QCheckBox)
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtGui import QColor, QFont

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
                        move_desc = f"Plate <b>{p+1}</b> {d_name}"
                        new_path = path + [(move_desc, state_str)]
                        queue.append((next_tuple, new_path))
                        
    return None

class BlockEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, 
                            QEvent.Type.MouseButtonDblClick, QEvent.Type.KeyPress, QEvent.Type.Wheel):
            return True
        return False

class LockpickingSolverKDETest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gothic 1 Remake Lockpicking Tool")
        self.resize(800, 600)
        
        self.block_filter = BlockEventFilter()
        self.num_plates = 5
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        
        # Setup Group
        self.setup_group = QWidget()
        self.main_layout.addWidget(self.setup_group)
        self.setup_layout = QVBoxLayout(self.setup_group)
        self.setup_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_start_positions()
        
        from PyQt6.QtWidgets import QFrame
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        self.setup_layout.addWidget(divider)
        
        self.create_behaviors()
        
        self.create_buttons()
        self.create_output()

    def create_start_positions(self):
        num_plates_layout = QHBoxLayout()
        num_plates_layout.addWidget(QLabel("Number of Plates:"))
        self.num_plates_cb = QComboBox()
        self.num_plates_cb.addItems([str(x) for x in range(3, 11)])
        self.num_plates_cb.setCurrentText("5")
        self.num_plates_cb.currentTextChanged.connect(self.update_num_plates)
        self.num_plates_cb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        num_plates_layout.addWidget(self.num_plates_cb)
        num_plates_layout.addStretch()
        self.setup_layout.addLayout(num_plates_layout)
        
        layout = QHBoxLayout()
        self.start_spins = []
        self.start_labels = []
        for i in range(10):
            lbl = QLabel(f"Piston {i+1}:")
            layout.addWidget(lbl)
            self.start_labels.append(lbl)
            spin = QSpinBox()
            spin.setRange(1, 7)
            spin.setValue(4)
            spin.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            spin.lineEdit().selectionChanged.connect(lambda s=spin: s.lineEdit().deselect())
            layout.addWidget(spin)
            self.start_spins.append(spin)
            
            if i >= 5:
                lbl.setVisible(False)
                spin.setVisible(False)
                
        layout.addStretch()
        self.setup_layout.addLayout(layout)

    def create_behaviors(self):
        behavior_widget = QWidget()
        from PyQt6.QtWidgets import QGridLayout
        layout = QGridLayout(behavior_widget)
        
        layout.addWidget(QLabel("Moving... \\ Affects..."), 0, 0)
        self.behavior_col_labels = []
        self.behavior_row_labels = []
        for i in range(10):
            lbl_col = QLabel(f"Plate {i+1}")
            layout.addWidget(lbl_col, 0, i+1)
            self.behavior_col_labels.append(lbl_col)
            
            lbl_row = QLabel(f"Moving Plate {i+1}")
            layout.addWidget(lbl_row, i+1, 0)
            self.behavior_row_labels.append(lbl_row)
            
            if i >= 5:
                lbl_col.setVisible(False)
                lbl_row.setVisible(False)
            
        self.behavior_cbs = []
        options = ["None", "Same", "Opposite"]
        bold_font = QFont()
        bold_font.setBold(True)
        for i in range(10):
            row_cbs = []
            for j in range(10):
                cb = QComboBox()
                cb.addItems(options)
                cb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                
                cb.setItemData(0, bold_font, Qt.ItemDataRole.FontRole)
                cb.setItemData(1, bold_font, Qt.ItemDataRole.FontRole)
                cb.setItemData(2, bold_font, Qt.ItemDataRole.FontRole)
                cb.setItemData(0, QColor("black"), Qt.ItemDataRole.ForegroundRole)
                cb.setItemData(1, QColor("#2e7d32"), Qt.ItemDataRole.ForegroundRole)
                cb.setItemData(2, QColor("#c62828"), Qt.ItemDataRole.ForegroundRole)
                
                if i == j:
                    from PyQt6.QtWidgets import QSizePolicy
                    cb.setCurrentText("Same")
                    cb.setStyleSheet("QComboBox { color: #2e7d32; font-weight: bold; background-color: rgba(128, 128, 128, 60); border: 1px solid palette(mid); border-bottom: 2px solid palette(mid); border-radius: 5px; padding: 4px 8px; margin: 3px 1px 2px 1px; } QComboBox:hover { border: 1px solid #3daee9; background-color: rgba(128, 128, 128, 80); } QComboBox::drop-down { border: none; width: 0px; }")
                    cb.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                    cb.installEventFilter(self.block_filter)
                else:
                    cb.setCurrentText("None")
                    cb.setStyleSheet("QComboBox { color: black; font-weight: bold; }")
                    cb.currentTextChanged.connect(self.update_cb_color)
                    
                layout.addWidget(cb, i+1, j+1)
                row_cbs.append(cb)
                
                if i >= 5 or j >= 5:
                    cb.setVisible(False)
                    
            self.behavior_cbs.append(row_cbs)
            
        layout.setRowStretch(11, 1)
        self.setup_layout.addWidget(behavior_widget)

    def update_num_plates(self, text):
        self.num_plates = int(text)
        
        for i in range(10):
            visible = (i < self.num_plates)
            self.start_labels[i].setVisible(visible)
            self.start_spins[i].setVisible(visible)
            self.behavior_col_labels[i].setVisible(visible)
            self.behavior_row_labels[i].setVisible(visible)
            
            for j in range(10):
                self.behavior_cbs[i][j].setVisible(i < self.num_plates and j < self.num_plates)

    def update_cb_color(self, text):
        cb = self.sender()
        if text == "Same":
            cb.setStyleSheet("QComboBox { color: #2e7d32; font-weight: bold; }")
        elif text == "Opposite":
            cb.setStyleSheet("QComboBox { color: #c62828; font-weight: bold; }")
        else:
            cb.setStyleSheet("QComboBox { color: black; font-weight: bold; }")

    def create_buttons(self):
        layout = QHBoxLayout()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        
        load_btn = QPushButton("Load Default Example")
        load_btn.clicked.connect(self.load_default_example)
        
        solve_btn = QPushButton("Solve Puzzle")
        solve_btn.clicked.connect(self.solve_puzzle)
        
        self.toggle_setup_btn = QPushButton("Hide Setup")
        self.toggle_setup_btn.setCheckable(True)
        self.toggle_setup_btn.toggled.connect(self.toggle_setup)
        
        layout.addWidget(reset_btn)
        layout.addWidget(load_btn)
        layout.addWidget(solve_btn)
        layout.addWidget(self.toggle_setup_btn)
        layout.addStretch()
        self.main_layout.addLayout(layout)

    def toggle_setup(self, checked):
        self.setup_group.setVisible(not checked)
        self.toggle_setup_btn.setText("Show Setup" if checked else "Hide Setup")

    def create_output(self):
        group = QGroupBox("Solution Output")
        layout = QVBoxLayout(group)
        
        self.output_table = QTableWidget()
        self.output_table.setColumnCount(3)
        self.output_table.setHorizontalHeaderLabels(["Step", "Action", "State"])
        self.output_table.setAlternatingRowColors(True)
        self.output_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.output_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.output_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.output_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.output_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.output_table.verticalHeader().setVisible(False)
        self.output_table.itemClicked.connect(self.toggle_bookmark)
        self.bookmarked_rows = set()
        
        layout.addWidget(self.output_table)
        self.main_layout.addWidget(group, stretch=1)

    def reset_defaults(self):
        self.resize(800, 600)
        if self.toggle_setup_btn.isChecked():
            self.toggle_setup_btn.setChecked(False)
        self.num_plates_cb.setCurrentText("5")
        self.output_table.setRowCount(0)
        if hasattr(self, 'bookmarked_rows'):
            self.bookmarked_rows.clear()
        
        for i in range(10):
            self.start_spins[i].setValue(4)
            for j in range(10):
                if i == j:
                    self.behavior_cbs[i][j].setCurrentText("Same")
                else:
                    self.behavior_cbs[i][j].setCurrentText("None")

    def load_default_example(self):
        self.num_plates_cb.setCurrentText("6")
        default_start = [6, 1, 1, 6, 1, 4]
        for i, val in enumerate(default_start):
            self.start_spins[i].setValue(val)
            
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
                    self.behavior_cbs[i][j].setCurrentText("Same")
                else:
                    self.behavior_cbs[i][j].setCurrentText("None")
                    
        for i in range(6):
            for j in range(6):
                self.behavior_cbs[i][j].setCurrentText(default_behaviors[i][j])

    def solve_puzzle(self):
        self.output_table.setRowCount(0)
        if hasattr(self, 'bookmarked_rows'):
            self.bookmarked_rows.clear()
        
        start_state = [spin.value() for spin in self.start_spins[:self.num_plates]]
        behaviors = []
        for i in range(self.num_plates):
            row = []
            for j in range(self.num_plates):
                val = self.behavior_cbs[i][j].currentText()
                if val == "Same":
                    row.append(1)
                elif val == "Opposite":
                    row.append(-1)
                else:
                    row.append(0)
            behaviors.append(row)
            
        path = solve_bfs(start_state, behaviors)
        
        if path is not None:
            # Compress path
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
            
            # We add start state as row 0
            self.output_table.setRowCount(len(compressed_path) + 1)
            
            start_str = ", ".join(map(str, start_state))
            self.add_table_row(0, "Start", "-", start_str)
            
            current_step = 1
            for i, (move_desc, state_str, num_moves) in enumerate(compressed_path):
                self.add_table_row(i + 1, str(current_step), move_desc, state_str)
                
                # Check if this compressed action covers a multiple of 10
                for k in range(current_step, current_step + num_moves):
                    if k % 10 == 0:
                        self.toggle_bookmark_by_row(i + 1)
                        break
                        
                current_step += num_moves
                
            if not self.toggle_setup_btn.isChecked():
                self.toggle_setup_btn.setChecked(True)
                
            # Resize to fit max 15 steps cleanly, without endlessly expanding
            items_to_fit = min(len(compressed_path) + 1, 15)
            target_height = 120 + (items_to_fit * 32)
            if self.height() < target_height:
                self.resize(self.width(), target_height)
        else:
            self.output_table.setRowCount(1)
            self.add_table_row(0, "-", "No solution found for this configuration.", "-")

    def add_table_row(self, row_idx, step_text, action_text, state_text):
        item_step = QTableWidgetItem(step_text)
        item_step.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_table.setItem(row_idx, 0, item_step)
        
        item_action = QTableWidgetItem() # Empty item for background color
        self.output_table.setItem(row_idx, 1, item_action)
        
        lbl = QLabel(action_text)
        if action_text == "-":
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl.setFixedWidth(130)
        lbl.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        hlayout = QHBoxLayout(container)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addStretch()
        hlayout.addWidget(lbl)
        hlayout.addStretch()
        
        self.output_table.setCellWidget(row_idx, 1, container)
        
        item_state = QTableWidgetItem(state_text)
        item_state.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Monospace", 11)
        font.setBold(True)
        item_state.setFont(font)
        self.output_table.setItem(row_idx, 2, item_state)

    def toggle_bookmark_by_row(self, row):
        from PyQt6.QtGui import QBrush, QColor
        if row in self.bookmarked_rows:
            self.bookmarked_rows.remove(row)
            for col in range(self.output_table.columnCount()):
                it = self.output_table.item(row, col)
                if it:
                    it.setBackground(QBrush())
                    it.setForeground(QBrush())
            w = self.output_table.cellWidget(row, 1)
            if w:
                lbl = w.findChild(QLabel)
                if lbl:
                    lbl.setStyleSheet("background: transparent;")
        else:
            self.bookmarked_rows.add(row)
            for col in range(self.output_table.columnCount()):
                it = self.output_table.item(row, col)
                if it:
                    it.setBackground(QColor("#4a7c59"))
                    it.setForeground(QColor("white"))
            w = self.output_table.cellWidget(row, 1)
            if w:
                lbl = w.findChild(QLabel)
                if lbl:
                    lbl.setStyleSheet("background: transparent; color: white;")

    def toggle_bookmark(self, item):
        self.toggle_bookmark_by_row(item.row())
        self.output_table.clearSelection()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockpickingSolverKDETest()
    window.show()
    sys.exit(app.exec())
