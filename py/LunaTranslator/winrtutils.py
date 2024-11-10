from ctypes import (
    c_uint,
    c_bool,
    c_wchar_p,
    CDLL,
    c_size_t,
    CFUNCTYPE,
    c_void_p,
    cast,
    POINTER,
    c_char,
)
from ctypes.wintypes import HANDLE
import platform, gobject, threading

try:
    if platform.system() != "Windows" or int(platform.version().split(".")[0]) <= 6:
        raise Exception()

    winrtutilsdll = CDLL(gobject.GetDllpath(("winrtutils32.dll", "winrtutils64.dll")))
except:
    winrtutilsdll = 0

if winrtutilsdll:

    _OCR_f = winrtutilsdll.OCR
    _OCR_f.argtypes = c_void_p, c_size_t, c_wchar_p, c_wchar_p, c_void_p

    _check_language_valid = winrtutilsdll.check_language_valid
    _check_language_valid.argtypes = (c_wchar_p,)
    _check_language_valid.restype = c_bool

    _getlanguagelist = winrtutilsdll.getlanguagelist
    _getlanguagelist.argtypes = (c_void_p,)

    def getlanguagelist():
        ret = []
        _getlanguagelist(CFUNCTYPE(None, c_wchar_p)(ret.append))
        return ret

    def OCR_f(data, lang, space):
        ret = []

        def cb(x1, y1, x2, y2, text):
            ret.append((text, x1, y1, x2, y2))

        t = threading.Thread(
            target=_OCR_f,
            args=(
                data,
                len(data),
                lang,
                space,
                CFUNCTYPE(None, c_uint, c_uint, c_uint, c_uint, c_wchar_p)(cb),
            ),
        )
        t.start()
        t.join()
        # 如果不这样，就会在在ui线程执行时，BitmapDecoder::CreateAsync(memoryStream).get()等Async函数会导致阻塞卡住。
        return ret

    _winrt_capture_window = winrtutilsdll.winrt_capture_window
    _winrt_capture_window.argtypes = c_void_p, c_void_p

    def winrt_capture_window(hwnd):
        ret = []

        def cb(ptr, size):
            ret.append(cast(ptr, POINTER(c_char))[:size])

        _winrt_capture_window(hwnd, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
        if len(ret):
            return ret[0]
        return None

    livecaption_start = winrtutilsdll.livecaption_start
    livecaption_start.argtypes = (c_void_p,)
    livecaption_start.restype = HANDLE
    livecaption_stop = winrtutilsdll.livecaption_stop
    livecaption_stop.argtypes = (HANDLE,)
    livecaption_isrunning = winrtutilsdll.livecaption_isrunning
    livecaption_isrunning.restype = c_bool
