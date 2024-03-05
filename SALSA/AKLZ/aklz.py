from __future__ import annotations

import os
import ctypes
from typing import Union


class BufWSize(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int),
                ("buffer", ctypes.POINTER(ctypes.c_char))]


class Aklz:
    def __init__(self):
        dll_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LIB', 'AKLZ.dll')
        self.dll = ctypes.cdll.LoadLibrary(dll_path)

        self.Decompress = self.dll.decompress
        self.Decompress.argtypes = ctypes.c_void_p, ctypes.c_void_p
        self.Decompress.restype = ctypes.c_int

        self.IsCompressed = self.dll.is_compressed
        self.IsCompressed.argtypes = (ctypes.POINTER(ctypes.c_char), )
        self.IsCompressed.restype = ctypes.c_int

        self.Compress = self.dll.compress
        self.Compress.argtypes = ctypes.c_void_p, ctypes.c_void_p
        self.Compress.restype = ctypes.c_int

    # ----------------- #
    # Compression Check #
    # ----------------- #

    @classmethod
    def is_compressed(cls, buffer_in: bytearray):
        a = cls()
        p = ctypes.c_char_p(bytes(buffer_in))
        p2 = ctypes.cast(p, ctypes.POINTER(ctypes.c_char))
        result = a.IsCompressed(p2)
        return result == 0

    # ------------------ #
    # Decompress Methods #
    # ------------------ #

    @classmethod
    def decompress(cls, buffer_in: bytearray, verbose=False):
        a = cls()
        return a._decompress(buffer_in)

    @classmethod
    def decompress_from_file(cls, filepath_in) -> bytearray:
        a = cls()
        return a._file_decompress(source=filepath_in)

    @classmethod
    def decompress_to_file(cls, bytes_in: bytearray, filepath_out: str) -> None:
        a = cls()
        a._file_decompress(source=bytes_in, filepath_out=filepath_out)

    @classmethod
    def decompress_from_file_to_file(cls, filepath_in: str, filepath_out: str) -> None:
        a = cls()
        a._file_decompress(source=filepath_in, filepath_out=filepath_out)

    def _file_decompress(self, source: Union[bytearray, str] = None, filepath_out: Union[None, str] = None) -> Union[None, bytearray]:
        if isinstance(source, str):
            with open(source, 'rb') as file_h:
                source = file_h.read()
        result = self._decompress(source)
        if filepath_out is None:
            return result
        with open(filepath_out, 'wb') as file_h:
            file_h.write(bytes(result))

    def _decompress(self, buffer_in):
        p = ctypes.c_char_p(bytes(buffer_in))
        p2 = ctypes.cast(p, ctypes.POINTER(ctypes.c_char))
        buf_in = BufWSize(len(buffer_in), p2)
        buf_out = BufWSize()
        result = self.Decompress(ctypes.addressof(buf_in), ctypes.addressof(buf_out))
        if result != 0:
            print("Decompressed failed")
        decompressed = bytearray(ctypes.string_at(buf_out.buffer, size=buf_out.size))
        return decompressed

    # ---------------- #
    # Compress Methods #
    # ---------------- #

    @classmethod
    def compress(cls, buffer_in: bytearray):
        a = cls()
        return a._compress(buffer_in)

    @classmethod
    def compress_from_file(cls, filepath_in) -> bytearray:
        a = cls()
        return a._file_compress(source=filepath_in)

    @classmethod
    def compress_to_file(cls, bytes_in: bytearray, filepath_out: str) -> None:
        a = cls()
        a._file_compress(source=bytes_in, filepath_out=filepath_out)

    @classmethod
    def compress_from_file_to_file(cls, filepath_in: str, filepath_out: str) -> None:
        a = cls()
        a._file_compress(source=filepath_in, filepath_out=filepath_out)

    def _file_compress(self, source: Union[bytearray, str] = None, filepath_out: Union[None, str] = None) -> Union[None, bytearray]:
        if isinstance(source, str):
            with open(source, 'rb') as file_h:
                source = file_h.read()
        result = self._compress(source)
        if filepath_out is None:
            return result
        with open(filepath_out, 'wb') as file_h:
            file_h.write(bytes(result))

    def _compress(self, buffer_in):
        p = ctypes.c_char_p(bytes(buffer_in))
        p2 = ctypes.cast(p, ctypes.POINTER(ctypes.c_char))
        buf_in = BufWSize(len(buffer_in), p2)
        buf_out = BufWSize()
        result = self.Decompress(ctypes.addressof(buf_in), ctypes.addressof(buf_out))
        if result != 0:
            print("Compression failed")
        compressed = bytearray(ctypes.string_at(buf_out.buffer, size=buf_out.size))
        return compressed


if __name__ == '__main__':
    filename = os.path.join(os.path.curdir, "a002a.mld")
    file_out = os.path.join(os.path.curdir, "a002a_d.mld")
    if not os.path.exists(filename):
        print('Please put test_file.test in this directory if you wish to test this module')

    with open(filename, 'rb') as fh:
        file = bytearray(fh.read())

    aklz = Aklz()
    print('Decompressing')
    file_d = aklz.decompress(buffer_in=file)

    with open(file_out, 'wb') as fh:
        fh.write(file_d)

    print('Recompressing')
    file_dc = aklz.compress(buffer_in=file_d)

    print('Decompressing the recompressed file')
    file_dcd = aklz.decompress(buffer_in=file_dc)

    decomp_same = True
    if len(file_d) != len(file_dcd):
        decomp_same = False

    for i in range(len(file_d)):
        if file_d[i] != file_dcd[i]:
            decomp_same = False

    if decomp_same:
        print('File successfully decompression, recompression, and decompression again.')
    else:
        print('File was not successfully decompressed, recompressed and decompressed again, Please check for errors')