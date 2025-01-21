[working-directory: 'src/ocean_optics']
compile:
    uv run pyside6-uic main_window.ui --output ui_main_window.py

design:
    uv run designer src/ocean_optics/main_window.ui
