"""Entradas nativas usadas pelo Drop; carregar somente ao abrir o aplicativo."""
import ctypes
from ctypes import wintypes


class WindowsInput:
    def __init__(self):
        self.u = ctypes.WinDLL("user32", use_last_error=True)
        assinaturas = {
            "GetForegroundWindow": ([], wintypes.HWND),
            "GetAncestor": ([wintypes.HWND, wintypes.UINT], wintypes.HWND),
            "GetCursorPos": ([ctypes.POINTER(wintypes.POINT)], wintypes.BOOL),
            "SetCursorPos": ([ctypes.c_int, ctypes.c_int], wintypes.BOOL),
            "mouse_event": ([wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                              wintypes.DWORD, ctypes.c_size_t], None),
            "keybd_event": ([wintypes.BYTE, wintypes.BYTE, wintypes.DWORD,
                              ctypes.c_size_t], None),
        }
        for nome, (argumentos, retorno) in assinaturas.items():
            funcao = getattr(self.u, nome)
            funcao.argtypes, funcao.restype = argumentos, retorno

    def foco(self):
        return self.u.GetForegroundWindow()

    def raiz(self, hwnd):
        return self.u.GetAncestor(hwnd, 2)

    def posicao(self):
        ponto = wintypes.POINT()
        if not self.u.GetCursorPos(ctypes.byref(ponto)):
            raise ctypes.WinError(ctypes.get_last_error())
        return ponto.x, ponto.y

    def mover(self, x, y):
        if not self.u.SetCursorPos(x, y):
            raise ctypes.WinError(ctypes.get_last_error())

    def mouse_down(self):
        self.u.mouse_event(0x0002, 0, 0, 0, 0)

    def mouse_up(self):
        self.u.mouse_event(0x0004, 0, 0, 0, 0)

    def espaco_down(self):
        self.u.keybd_event(0x20, 0x39, 0, 0)

    def espaco_up(self):
        self.u.keybd_event(0x20, 0x39, 2, 0)

    def tecla_down(self, tecla):
        """Seleciona 1/2/3 no jogo; scan codes PC set 1."""
        if tecla not in ("1", "2", "3"):
            raise ValueError("Somente as teclas 1, 2 e 3 sao permitidas.")
        vk, scan = {"1": (0x31, 0x02), "2": (0x32, 0x03),
                    "3": (0x33, 0x04)}[tecla]
        self.u.keybd_event(vk, scan, 0, 0)

    def tecla_up(self, tecla):
        if tecla not in ("1", "2", "3"):
            raise ValueError("Somente as teclas 1, 2 e 3 sao permitidas.")
        vk, scan = {"1": (0x31, 0x02), "2": (0x32, 0x03),
                    "3": (0x33, 0x04)}[tecla]
        self.u.keybd_event(vk, scan, 2, 0)
