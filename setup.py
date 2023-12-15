import sys
from cx_Freeze import setup, Executable


# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"



build_exe_options = {"include_files": ["lib", "audio_beat.ico"]}

executables = [
        Executable(
            "audio_beat.py",
            base=base,
            icon="audio_beat.ico",
        ),
    ]



setup(
    name="audio_beat",
    version="0.1",
    description="Audio Beat",
    options={"build_exe": build_exe_options},
    executables=executables,
)
