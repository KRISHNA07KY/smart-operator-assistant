"""build_exe.py
PyInstaller build script for Caterpillar Smart Operator Assistant.
"""
import PyInstaller.__main__
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MODELS_DIR = os.path.join(BASE_DIR, "models")

args = [
    os.path.join(BASE_DIR, "main.py"),
    "--name=CatOperatorAssistant",
    "--noconfirm",
    "--windowed",  # Suppress background console window
    f"--add-data={FRONTEND_DIST};frontend/dist",
    f"--add-data={ASSETS_DIR};assets",
    f"--add-data={MODELS_DIR};models",
    "--hidden-import=PySide6.QtWebEngineWidgets",
    "--hidden-import=PySide6.QtWebEngineCore",
    "--hidden-import=PySide6.QtWebChannel",
    "--hidden-import=PySide6.QtSvg",
    "--hidden-import=PySide6.QtNetwork",
    "--hidden-import=backend",
    "--hidden-import=backend.app",
    "--hidden-import=backend.dummy_ml",
    "--hidden-import=backend.bridge",
    "--hidden-import=widgets",
    "--hidden-import=widgets.header_bar",
    "--hidden-import=widgets.tab_tasks",
    "--hidden-import=widgets.tab_safety",
    "--hidden-import=widgets.tab_estimator",
    "--hidden-import=widgets.tab_telemetry",
    "--hidden-import=widgets.tab_training",
    "--hidden-import=utils.icon_manager",
    "--hidden-import=config",
    "--clean",
]

print("Running PyInstaller with arguments:")
for a in args:
    print(" ", a)

PyInstaller.__main__.run(args)
print("\n[BUILD SUCCESSFUL] CatOperatorAssistant build completed!")
