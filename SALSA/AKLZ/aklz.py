from __future__ import annotations

import os
import ctypes

from AKLZ.LIB import aklz_fast, aklz_slow

aklz_lib = 'AKLZ.dll'


class BufWSize(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int),
                ("buffer", ctypes.POINTER(ctypes.c_char))]


class Aklz:
    def __init__(self, use_slow=False):
        self.use_slow = use_slow
        if os.name != 'nt' or use_slow:
            self._decompress = aklz_slow.decompress
            self._compress = aklz_slow.compress
            self._is_compressed = aklz_slow.is_compressed

        else:
            self._decompress = aklz_fast.decompress
            self._compress = aklz_fast.compress
            self._is_compressed = aklz_fast.is_compressed

    @classmethod
    def decompress(cls, buffer_in: bytearray, use_slow=False):
        a = cls(use_slow)
        return a._decompress(buffer_in)

    @classmethod
    def compress(cls, buffer_in: bytearray, use_slow=False):
        a = cls(use_slow)
        return a._compress(buffer_in)

    @classmethod
    def is_compressed(cls, buffer_in: bytearray, use_slow=False):
        a = cls(use_slow)
        return a._is_compressed(buffer_in)


if __name__ == '__main__':
    filename = os.path.join(os.path.curdir, "a002a.mld")
    file_out = os.path.join(os.path.curdir, "a002a_d.mld")
    if not os.path.exists(filename):
        print('Please put a002a.mld in this directory if you wish to test this module')

    with open(filename, 'rb') as fh:
        file = bytearray(fh.read())

    file_d = bytearray()
    file_dc = bytearray()
    file_dcd = bytearray()

    if os.name == 'nt':
        print('Testing python implementations')

        print('Checking for compression')
        print(f'File is compressed: {Aklz.is_compressed(file, use_slow=True)}')

        print('Decompressing')
        file_d = Aklz.decompress(buffer_in=file, use_slow=True)

        with open(file_out, 'wb') as fh:
            fh.write(file_d)

        print('Recompressing')
        file_dc = Aklz.compress(buffer_in=file_d, use_slow=True)

        print('Decompressing the recompressed file')
        file_dcd = Aklz.decompress(buffer_in=file_dc, use_slow=True)

        decomp_same = True
        if len(file_d) != len(file_dcd):
            decomp_same = False

        for i in range(len(file_d)):
            if file_d[i] != file_dcd[i]:
                decomp_same = False

        if decomp_same:
            print('File successfully decompressed, recompressed, and decompressed again.')
        else:
            print(
                'File was not successfully decompressed, recompressed and decompressed again, Please check for errors')

        print('\nTesting dll implementation')

    else:
        print('No dll implementation available, testing python implementation')

    print('Decompressing')
    file_d = Aklz.decompress(buffer_in=file)

    with open(file_out, 'wb') as fh:
        fh.write(file_d)

    print('Recompressing')
    file_dc = Aklz.compress(buffer_in=file_d)

    print('Decompressing the recompressed file')
    file_dcd = Aklz.decompress(buffer_in=file_dc)

    decomp_same = True
    if len(file_d) != len(file_dcd):
        decomp_same = False

    for i in range(len(file_d)):
        if file_d[i] != file_dcd[i]:
            decomp_same = False

    if decomp_same:
        print('File successfully decompressed, recompressed, and decompressed again.')
    else:
        print('File was not successfully decompressed, recompressed and decompressed again, Please check for errors')