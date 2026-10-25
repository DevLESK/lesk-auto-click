"""Observa cliques físicos no Windows sem bloquear ou gerar entradas."""
import ctypes
import sys
import threading
from ctypes import wintypes


class PhysicalMouseListener:
    def __init__(self, callback):
        self.callback = callback
        self._ready = threading.Event()
        self._thread = None
        self._thread_id = None
        self._error = None
        self._user32 = None
        self._proc = None

    def _receber(self, mensagem, flags):
        # LLMHF_INJECTED: nunca interpretar os cliques sintéticos como físicos.
        if flags & 1:
            return
        botao = {0x0201: "left", 0x0204: "right"}.get(mensagem)
        if botao:
            self.callback(botao)

    def start(self):
        if sys.platform != "win32":
            return  # O aplicativo é distribuído para Windows.
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        if not self._ready.wait(3):
            raise RuntimeError("Tempo esgotado ao observar o mouse físico")
        if self._error:
            raise RuntimeError("Não foi possível observar o mouse físico") from self._error

    def _run(self):
        hook = None
        try:
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            self._user32 = user32
            lresult = ctypes.c_ssize_t
            callback_type = ctypes.WINFUNCTYPE(lresult, ctypes.c_int,
                                                wintypes.WPARAM, wintypes.LPARAM)

            class MouseData(ctypes.Structure):
                _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD),
                            ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                            ("dwExtraInfo", ctypes.c_size_t)]

            user32.SetWindowsHookExW.argtypes = [ctypes.c_int, callback_type,
                                                wintypes.HINSTANCE, wintypes.DWORD]
            user32.SetWindowsHookExW.restype = wintypes.HHOOK
            user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int,
                                              wintypes.WPARAM, wintypes.LPARAM]
            user32.CallNextHookEx.restype = lresult
            user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
            user32.UnhookWindowsHookEx.restype = wintypes.BOOL
            user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                           wintypes.UINT, wintypes.UINT]
            user32.GetMessageW.restype = wintypes.BOOL
            user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                            wintypes.UINT, wintypes.UINT, wintypes.UINT]
            user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT,
                                                 wintypes.WPARAM, wintypes.LPARAM]
            user32.PostThreadMessageW.restype = wintypes.BOOL
            kernel32.GetCurrentThreadId.restype = wintypes.DWORD
            kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
            kernel32.GetModuleHandleW.restype = wintypes.HMODULE

            def observar(code, mensagem, dados):
                if code >= 0:
                    try:
                        info = ctypes.cast(dados, ctypes.POINTER(MouseData)).contents
                        self._receber(mensagem, info.flags)
                    except Exception:
                        # Um erro do consumidor não deve bloquear o mouse do usuário.
                        pass
                return user32.CallNextHookEx(None, code, mensagem, dados)

            self._proc = callback_type(observar)  # Manter vivo enquanto o hook existe.
            self._thread_id = kernel32.GetCurrentThreadId()
            msg = wintypes.MSG()
            user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
            hook = user32.SetWindowsHookExW(14, self._proc,
                                            kernel32.GetModuleHandleW(None), 0)
            if not hook:
                raise ctypes.WinError(ctypes.get_last_error())
            self._ready.set()
            while True:
                resultado = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if resultado == -1:
                    raise ctypes.WinError(ctypes.get_last_error())
                if resultado == 0:
                    break
        except Exception as exc:
            self._error = exc
        finally:
            if hook:
                self._user32.UnhookWindowsHookEx(hook)
            self._ready.set()

    def stop(self):
        if self._thread and self._thread.is_alive() and self._user32 and self._thread_id:
            self._user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            self._thread.join(timeout=1)
