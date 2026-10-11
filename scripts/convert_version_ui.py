# not very good ai attempt, prob not gonna use it again 

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QVariantAnimation, QEasingCurve, QPropertyAnimation, QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QScrollArea, QMenu, QMessageBox, QSizePolicy,
    QGraphicsOpacityEffect
)

# Image paths are relative to this script. Replace these with your own files.
# The same loader icons are reused for every row.
ICON_DIR = Path(__file__).resolve().parent / "icons"
REFRESH_ICON_PATH = ICON_DIR / "refresh.png"
COMPATIBLE_ICON_PATH = ICON_DIR / "compatible.png"  # green check
INCOMPATIBLE_ICON_PATH = ICON_DIR / "incompatible.png"  # red cross
MOD_ICON_PATH = ICON_DIR / "fabric.png"  # square image shown for each mod
BUILT_FOR_LOADER_ICON_PATH = ICON_DIR / "fabric.png"  # loader image at far right
VERSION_ICON_PATH = ICON_DIR / "fabric.png"  # top-right Minecraft-version icon

# Catppuccin Mocha palette
BASE = "#1e1e2e"
MANTLE = "#181825"
CRUST = "#11111b"
SURFACE0 = "#313244"
SURFACE1 = "#45475a"
TEXT = "#cdd6f4"
SUBTEXT = "#a6adc8"
GREEN = "#a6e3a1"
RED = "#f38ba8"
BLUE = "#89b4fa"
MAUVE = "#cba6f7"


class AnimatedButton(QPushButton):
    """A QPushButton with smooth Catppuccin hover/press colour transitions."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._normal = QColor(SURFACE0)
        self._hover = QColor(SURFACE1)
        self._pressed = QColor(MAUVE)
        self._text_normal = TEXT
        self._text_pressed = CRUST
        self._current = QColor(self._normal)
        self._target = QColor(self._normal)
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(170)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_animated_colour)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"QPushButton {{ color:{self._text_normal}; background:{self._normal.name()}; "
            f"border:1px solid {SURFACE1}; border-radius:7px; padding:8px 10px; text-align:left; }}"
        )

    def _set_animated_colour(self, colour):
        self._current = QColor(colour)
        text_colour = self._text_pressed if self._target == self._pressed else self._text_normal
        self.setStyleSheet(
            f"QPushButton {{ color:{text_colour}; background:{self._current.name()}; "
            f"border:1px solid {SURFACE1}; border-radius:7px; padding:8px 10px; text-align:left; }}"
        )

    def _animate_to(self, colour):
        self._target = QColor(colour)
        self._animation.stop()
        self._animation.setStartValue(self._current)
        self._animation.setEndValue(self._target)
        self._animation.start()

    def enterEvent(self, event):
        self._animate_to(self._hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(self._normal)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_to(self._pressed)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._animate_to(self._hover if self.underMouse() else self._normal)




def load_icon(path):
    """Return a Qt icon for an existing image path, otherwise an empty icon."""
    path = Path(path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if path.is_file():
        icon = QIcon(str(path))
        if not icon.isNull():
            return icon
    print(f"Icon not found or unreadable: {path}")
    return QIcon()


def icon_label(icon, fallback, size=20, color=TEXT):
    label = QLabel()
    label.setFixedSize(size, size)
    if not icon.isNull():
        label.setPixmap(icon.pixmap(QSize(size, size)))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    else:
        label.setText(fallback)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {color}; font-weight: bold;")
    return label


class ModEntry(QFrame):
    def __init__(self, mod, icons, on_select, on_action, parent=None):
        super().__init__(parent)
        self.mod = mod
        self.icons = icons
        self.on_select = on_select
        self.on_action = on_action
        self.setObjectName("modEntry")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._row_normal = QColor(BASE)
        self._row_hover = QColor(SURFACE0)
        self._row_current = QColor(BASE)
        self._row_animation = QVariantAnimation(self)
        self._row_animation.setDuration(180)
        self._row_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._row_animation.valueChanged.connect(self._set_row_colour)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        compatible = bool(mod.get("compatible", True))
        check_icon = icons["compatible"] if compatible else icons["incompatible"]
        layout.addWidget(icon_label(check_icon, "✓" if compatible else "✕",
                                    color=GREEN if compatible else RED))

        mod_icon_label = QLabel()
        mod_icon_label.setFixedSize(42, 42)
        mod_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not icons["mod"].isNull():
            mod_icon_label.setPixmap(icons["mod"].pixmap(QSize(42, 42)))
        else:
            mod_icon_label.setText("MOD")
            mod_icon_label.setStyleSheet(
                f"background:{SURFACE1}; color:{SUBTEXT}; border-radius:6px;"
            )
        layout.addWidget(mod_icon_label)

        name = QLabel(mod["name"])
        name.setStyleSheet(f"color:{TEXT}; font-size:14px; font-weight:600;")
        name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(name, 1)

        loader_label = icon_label(
            icons["loader"], "◇", color=MAUVE
        )
        loader_label.setToolTip(f'Built for {mod.get("loader", "unknown")}')
        layout.addWidget(loader_label)

        # Clicking anywhere selects this mod.
        for widget in (self, mod_icon_label, name, loader_label):
            widget.mousePressEvent = self._make_click_handler(widget.mousePressEvent)

    def _set_row_colour(self, colour):
        self._row_current = QColor(colour)
        self.setStyleSheet(
            f"QFrame#modEntry {{ background:{self._row_current.name()}; "
            f"border:1px solid {SURFACE0}; border-radius:8px; }}"
        )

    def _animate_row(self, colour):
        self._row_animation.stop()
        self._row_animation.setStartValue(self._row_current)
        self._row_animation.setEndValue(QColor(colour))
        self._row_animation.start()

    def enterEvent(self, event):
        self._animate_row(self._row_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_row(self._row_normal)
        super().leaveEvent(event)

    def _make_click_handler(self, original_handler):
        def handler(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_select(self.mod)
            original_handler(event)
        return handler

    def contextMenuEvent(self, event):
        self.show_context_menu(event.pos())

    def show_context_menu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background:{SURFACE0}; color:{TEXT}; border:1px solid {SURFACE1}; padding:5px; }}
            QMenu::item {{ padding:7px 28px 7px 12px; border-radius:4px; }}
            QMenu::item:selected {{ background:{SURFACE1}; }}
        """)
        for label in ("Replace", "Switch version", "Switch loader", "Delete"):
            action = menu.addAction(label)
            action.triggered.connect(
                lambda checked=False, a=label: self.on_action(a, self.mod)
            )
        menu.exec(self.mapToGlobal(position))


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lightly Modded Compiler")
        self.resize(1050, 620)
        self.setMinimumSize(780, 450)

        # Each icon is loaded once and reused by every row.
        self.icons = {
            "refresh": load_icon(REFRESH_ICON_PATH),
            "compatible": load_icon(COMPATIBLE_ICON_PATH),
            "incompatible": load_icon(INCOMPATIBLE_ICON_PATH),
            "mod": load_icon(MOD_ICON_PATH),
            "loader": load_icon(BUILT_FOR_LOADER_ICON_PATH),
            "version": load_icon(VERSION_ICON_PATH),
        }

        # Demo rows. Replace with your real compatibility results and mod data.
        self.mods = [
            {"name": "Sodium", "version": "0.8.1", "loader": "Fabric", "compatible": True},
            {"name": "Lithium", "version": "0.20.0", "loader": "Fabric", "compatible": True},
            {"name": "FerriteCore", "version": "7.0.2", "loader": "Fabric", "compatible": True},
            {"name": "Entity Culling", "version": "1.7.4", "loader": "Fabric", "compatible": True},
            {"name": "ImmediatelyFast", "version": "1.6.0", "loader": "Fabric", "compatible": True},
            {"name": "ModernFix", "version": "5.24.0", "loader": "Forge", "compatible": False},
            {"name": "Dynamic FPS", "version": "3.9.4", "loader": "Fabric", "compatible": True},
            {"name": "Indium", "version": "1.0.36", "loader": "Fabric", "compatible": False},
            {"name": "Fabric API", "version": "0.136.0", "loader": "Fabric", "compatible": True},
            {"name": "Mod Menu", "version": "16.0.0", "loader": "Fabric", "compatible": True},
            {"name": "Iris", "version": "1.9.0", "loader": "Fabric", "compatible": True},
            {"name": "Zoomify", "version": "2.14.0", "loader": "Quilt", "compatible": False},
            {"name": "Continuity", "version": "3.0.0", "loader": "Fabric", "compatible": True},
            {"name": "Debugify", "version": "1.0.0", "loader": "Fabric", "compatible": True},
            {"name": "Cloth Config", "version": "20.0.0", "loader": "Fabric", "compatible": True},
            {"name": "YetAnotherConfigLib", "version": "4.0.0", "loader": "Fabric", "compatible": True},
            {"name": "No Chat Reports", "version": "2.9.0", "loader": "Fabric", "compatible": True},
            {"name": "AppleSkin", "version": "3.0.0", "loader": "Forge", "compatible": False},
            {"name": "Xaero's Minimap", "version": "25.2.0", "loader": "Fabric", "compatible": True},
            {"name": "Xaero's World Map", "version": "1.39.0", "loader": "Fabric", "compatible": True},
        ]
        self.selected_mod = None
        self.entry_widgets = []

        central = QWidget()
        central.setStyleSheet(f"background:{BASE}; color:{TEXT};")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # Top toolbar: refresh on left, Minecraft version on right.
        toolbar = QFrame()
        toolbar.setStyleSheet(f"background:{MANTLE}; border-radius:10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)

        refresh_button = AnimatedButton("Refresh")
        refresh_button.setIcon(self.icons["refresh"])
        refresh_button.setIconSize(QSize(20, 20))
        refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_button)
        toolbar_layout.addStretch(1)

        toolbar_layout.addWidget(icon_label(self.icons["version"], "▣", 22))
        version_label = QLabel("Minecraft 1.21.10")
        version_label.setStyleSheet(f"color:{TEXT}; font-weight:600;")
        toolbar_layout.addWidget(version_label)
        root.addWidget(toolbar)

        # Main panel: scroll list left, action buttons right.
        body = QHBoxLayout()
        body.setSpacing(10)
        root.addLayout(body, 1)

        list_panel = QFrame()
        list_panel.setStyleSheet(f"background:{MANTLE}; border-radius:10px;")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(10, 10, 10, 10)
        list_title = QLabel("Installed mods")
        list_title.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; font-weight:600;")
        list_layout.addWidget(list_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(
            f"QScrollArea {{ background:{MANTLE}; border:none; }}"
            f"QScrollBar:vertical {{ background:{BASE}; width:10px; margin:2px; }}"
            f"QScrollBar::handle:vertical {{ background:{SURFACE1}; min-height:24px; border-radius:5px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}"
        )
        self.rows_host = QWidget()
        self.rows_host.setStyleSheet(f"background:{MANTLE};")
        self.rows_layout = QVBoxLayout(self.rows_host)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(5)
        self.rows_layout.addStretch(1)
        self.scroll.setWidget(self.rows_host)
        list_layout.addWidget(self.scroll, 1)
        body.addWidget(list_panel, 1)

        actions_panel = QFrame()
        actions_panel.setFixedWidth(180)
        actions_panel.setStyleSheet(f"background:{MANTLE}; border-radius:10px;")
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setContentsMargins(12, 14, 12, 12)
        actions_title = QLabel("Actions")
        actions_title.setStyleSheet(f"color:{TEXT}; font-size:16px; font-weight:700;")
        actions_layout.addWidget(actions_title)

        for label, action_name in (
            ("Add mod", "Add mod"),
            ("Replace", "Replace"),
            ("Switch version", "Switch version"),
            ("Switch loader", "Switch loader"),
            ("Delete", "Delete"),
            ("Open folder", "Open folder"),
        ):
            button = AnimatedButton(label)
            button.clicked.connect(lambda checked=False, a=action_name: self.action(a))
            actions_layout.addWidget(button)
        actions_layout.addStretch(1)
        body.addWidget(actions_panel)

        self.setStyleSheet(self.styleSheet() + "QScrollArea { border:none; }")
        self.populate_entries()

    def populate_entries(self):
        # Remove existing rows, preserving the final stretch item.
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.entry_widgets.clear()

        for mod in self.mods:
            row = ModEntry(mod, self.icons, self.select_mod, self.entry_action)
            row.setStyleSheet(
                f"QFrame#modEntry {{ background:{BASE}; border:1px solid {SURFACE0}; border-radius:8px; }}"
            )
            self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)
            self.entry_widgets.append(row)
            # Brief fade-in makes refreshed/rebuilt lists feel less abrupt.
            effect = QGraphicsOpacityEffect(row)
            row.setGraphicsEffect(effect)
            fade = QPropertyAnimation(effect, b"opacity", row)
            fade.setDuration(220)
            fade.setStartValue(0.0)
            fade.setEndValue(1.0)
            fade.setEasingCurve(QEasingCurve.Type.OutCubic)
            row._fade_animation = fade  # keep the animation alive
            QTimer.singleShot(min(len(self.entry_widgets) * 12, 180), fade.start)

    def select_mod(self, mod):
        self.selected_mod = mod
        print("Selected:", mod["name"])

    def entry_action(self, action, mod):
        self.selected_mod = mod
        if action == "Delete":
            answer = QMessageBox.question(
                self, "Delete mod", f'Delete "{mod["name"]}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.mods.remove(mod)
                self.populate_entries()
        else:
            self.action(action, mod)

    def action(self, action, mod=None):
        mod = mod or self.selected_mod
        if action != "Add mod" and mod is None:
            QMessageBox.information(self, "Nothing selected", "Select a mod first.")
            return
        print(f'Action: {action}; mod: {mod["name"] if mod else "(none)"}')
        # Connect these actions to your existing compiler/mod-management logic.

    def refresh(self):
        print("Refresh clicked")
        # Reload your actual mod list, then call self.populate_entries().


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(f"""
        QWidget {{ background:{BASE}; color:{TEXT}; font-family:'Segoe UI'; font-size:12px; }}
        QToolTip {{ color:{TEXT}; background:{SURFACE0}; border:1px solid {SURFACE1}; padding:4px; }}
    """)
    window = App()
    window.setWindowOpacity(0.0)
    window.show()
    window_fade = QPropertyAnimation(window, b"windowOpacity", window)
    window_fade.setDuration(260)
    window_fade.setStartValue(0.0)
    window_fade.setEndValue(1.0)
    window_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    window._window_fade_animation = window_fade
    QTimer.singleShot(0, window_fade.start)
    sys.exit(app.exec())
