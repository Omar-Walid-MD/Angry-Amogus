import cx_Freeze

base = "Win32GUI"
executables = [cx_Freeze.Executable("main.py",base=base,icon="icon.ico",target_name="Angry Amogus.exe")]

cx_Freeze.setup(
    name="Angry Amogus",
    options={"build_exe": {"packages":["pygame"]}},
    executables = executables

    )
