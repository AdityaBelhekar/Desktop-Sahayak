import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction

# --- 1. The Main Application Window ---
class Avatar(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- 2. Setting Window Properties (Our Logic) ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # --- 3. Setting Up the Window's Size and a Placeholder ---
        self.setGeometry(200, 200, 250, 250)
        self.label = QLabel("Drag me!\nRight-click for options.", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: rgba(0, 0, 0, 70); color: white; font-size: 18px; border-radius: 10px;")
        self.setCentralWidget(self.label) # Set label as the main content

        # --- 4. Draggable Window Logic ---
        self.old_pos = None

        # --- 5. Initial State ---
        self.toggle_always_on_top(True) # Start as always on top by default

    # --- 6. Right-Click Context Menu ---
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # Action to toggle "Always on Top"
        always_on_top_action = QAction("Always on Top", self, checkable=True)
        always_on_top_action.setChecked(self.is_always_on_top())
        always_on_top_action.triggered.connect(self.toggle_always_on_top)
        context_menu.addAction(always_on_top_action)

        context_menu.addSeparator()

        # Action to quit the application
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        context_menu.addAction(quit_action)

        context_menu.exec(event.globalPos())

    def is_always_on_top(self):
        # Check if the WindowStaysOnTopHint flag is set
        return self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint

    def toggle_always_on_top(self, checked):
        flags = self.windowFlags()
        if checked:
            # Add the flag
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            # Remove the flag
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show() # Re-show the window to apply flag changes

    # --- 7. Mouse Events for Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()


# --- Running the Application ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    avatar_window = Avatar()
    avatar_window.show()
    sys.exit(app.exec())