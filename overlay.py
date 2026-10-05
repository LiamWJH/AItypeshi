import threading
import ctypes
import signal
import tkinter as tk

_user32 = ctypes.windll.user32

_GWL_EXSTYLE = -20
_GA_ROOT = 2
WS_EX_TRANSPARENT = 0x20
WS_EX_TOOLWINDOW = 0x80
WS_EX_NOACTIVATE = 0x08000000


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def apply_ex_styles(tk_widget, styles):
    hwnd = _user32.GetAncestor(tk_widget.winfo_id(), _GA_ROOT)
    current = _user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    _user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, current | styles)


class TextHud:
    def __init__(self, parent, text=" ", fg="cyan", bg="#101010",
                 font=("Consolas", 20)):
        self.var = tk.StringVar(value=text)
        tk.Label(parent, textvariable=self.var, fg=fg, bg=bg,
                 font=font).pack(padx=10, pady=10)

    def set(self, text):
        self.var.set(text)

class Overlay:
    """A borderless always-on-top window with a border drawn around its content.

    The window shrinks to fit the content, so the border hugs it.
    Put your components inside `overlay.body`.
    """

    def __init__(self, x=100, y=100, width=None, height=None, alpha=0.75,
                 bg="#101010", border_color="CadetBlue1", border_width=1,
                 click_through=True, topmost=True, transparent_bg=True,
                 poll_ms=200):
        enable_dpi_awareness()
        self.bg = bg
        self.poll_ms = poll_ms
        self.click_through = click_through
        self._alive = True

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", topmost)
        self.root.attributes("-alpha", alpha)

        self.root.config(bg=border_color)
        if transparent_bg:
            self.root.attributes("-transparentcolor", bg)  # content area see-through

        size = f"{width}x{height}" if width and height else ""
        self.root.geometry(f"{size}+{x}+{y}")

        self.body = tk.Frame(self.root, bg=bg)
        self.body.pack(fill="both", expand=True, padx=border_width, pady=border_width)

    def every(self, ms, fn, **args):
        def tick():
            if not self._alive:
                return
            fn(*args)
            if self._alive:
                self.root.after(ms, tick)
        self.root.after(ms, tick)

    def close(self, *_):
        self._alive = False
        self.root.destroy()

    def run(self):
        self.root.update_idletasks()

        styles = WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        if self.click_through:
            styles |= WS_EX_TRANSPARENT
        apply_ex_styles(self.root, styles)

        self.root.deiconify()


        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self.close)
        def wake():
            self.root.after(self.poll_ms, wake)
        wake()

        self.root.mainloop()
