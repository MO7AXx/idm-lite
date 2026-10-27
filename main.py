#!/usr/bin/env python3
"""IDM Lite entry point.

Double-click the .exe and the download manager opens.
"""
from __future__ import annotations

import os
import sys
import traceback


def _frozen_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hide_console() -> None:
    """Hide the console window so the app behaves like a normal GUI program.

    CPython's embedded initialiser needs a console object to attach its
    standard streams to, so we keep the console but hide its window.  When the
    app is started from a terminal we leave that terminal alone.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hwnd = kernel32.GetConsoleWindow()
        if not hwnd:
            return
        count = ctypes.c_ulong(0)
        if kernel32.GetConsoleProcessList(None, ctypes.byref(count)):
            if count.value > 1:
                return                      # someone else is using it
        user32.ShowWindow(hwnd, 0)           # SW_HIDE
    except Exception:
        pass


def main() -> int:
    _hide_console()
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "IDMLite.Desktop.1")
        except Exception:
            pass

    try:
        import tkinter as tk
        from idmlite.config import Config
        from idmlite.gui import MainWindow
        from idmlite.single import SingleInstance
    except Exception:
        # Last-ditch error box so a broken install is not silent.
        msg = traceback.format_exc()
        try:
            import tkinter as tk
            from tkinter import messagebox
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("IDM Lite — startup error",
                                 "IDM Lite could not start:\n\n" + msg[-1500:])
            r.destroy()
        except Exception:
            print(msg, file=sys.stderr)
        return 1

    # Only one copy may run: two engines would write to the same files and
    # repeat every notification.
    guard = SingleInstance()
    if not guard.acquire():
        guard.request_show()
        try:
            messagebox.showinfo("IDM Lite",
                                "IDM Lite is already running.\n"
                                "It has been brought to the front.")
        except Exception:
            pass
        return 0

    root = tk.Tk()
    config = Config()
    try:
        app = MainWindow(root, config)
        app._guard = guard
    except Exception:
        msg = traceback.format_exc()
        try:
            from tkinter import messagebox
            messagebox.showerror("IDM Lite — startup error", msg[-1500:])
        except Exception:
            print(msg, file=sys.stderr)
        root.destroy()
        guard.release()
        return 1

    # make sure the window is really visible when the app starts
    try:
        root.deiconify()
        root.lift()
    except Exception:
        pass

    try:
        root.mainloop()
    finally:
        try:
            guard.release()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
