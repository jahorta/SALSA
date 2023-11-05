import ctypes.wintypes as win
import ctypes as ct
import psutil
import threading
from dataclasses import dataclass
import datetime as dt
import queue as q
from SALSA.DolphinMemAccess.mem_page_file_access import *

GAMECODES = {
    'GEAE8P': 'Skies of Arcadia Legends (US)',
    'GEAP8P': 'Skies of Arcadia Legends (EU)',
    'GEAJ8P': 'Skies of Arcadia Legends (JP)'
}

process_name = "Dolphin.exe"


def ptr2addr(ptr: Union[str, bytearray]) -> bytearray:
    if isinstance(ptr, bytearray):
        ptr = ptr.hex()
    if '0x' in ptr:
        ptr = ptr[2:]
    if ptr[0] == '8':
        ptr = '0'+ptr[1:]
    return bytearray.fromhex(ptr)


@dataclass
class MemSegment:
    addr: str
    rss: int


@dataclass
class MemObject:
    addr: int
    size: int


class DolphinMemoryController:

    _pid: int = None
    _handle: win.HANDLE = None
    _mem1_addr: int = 0
    _mem2_addr: int = 0

    _refresh_thread = threading.Thread
    _last_access: dt.datetime
    _kill_q: q.SimpleQueue
    connected: bool = False

    def __init__(self):
        self.OpenProcess = ct.windll.kernel32.OpenProcess
        self.OpenProcess.argtypes = win.DWORD, win.BOOL, win.DWORD
        self.OpenProcess.restype = win.HANDLE

        self.ReadProcessMemory = ct.windll.kernel32.ReadProcessMemory
        self.ReadProcessMemory.argtypes = win.HANDLE, win.LPCVOID, win.LPVOID, ct.c_size_t, ct.POINTER(ct.c_size_t)
        self.ReadProcessMemory.restype = win.BOOL

        self.WriteProcessMemory = ct.windll.kernel32.WriteProcessMemory
        self.WriteProcessMemory.argtypes = win.HANDLE, win.LPVOID, win.LPCVOID, ct.c_size_t, ct.POINTER(ct.c_size_t)
        self.WriteProcessMemory.restype = win.BOOL

        self.CloseHandle = ct.windll.kernel32.CloseHandle
        self.CloseHandle.argtypes = [HANDLE]
        self.CloseHandle.restype = BOOL

    def get_process_info(self):
        procs = []
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            if proc.name() == process_name and proc.status() == psutil.STATUS_RUNNING:
                pid = proc.pid
                procs.append(pid)
                print(f'Dolphin PID: {pid}')

        if len(procs) == 0:
            print('No process named Dolphin.exe is running')
            return 0

        self._pid = procs[0]
        return 1

    def attach_to_dolphin(self):
        if self._pid is None:
            if self.get_process_info() == 0:
                return 0

        if self._handle is None:
            if self._get_handle() != 1:
                return 0

        self._get_dolphin_mems()
        if self._mem1_addr == 0:
            print('Unable to find regions, likely emulation has not started yet')
            return 2

        self.connected = True

        return 1

    def _get_handle(self):
        PROCESS_ALL_ACCESS = 0x1F0FFF
        self._handle = self.OpenProcess(PROCESS_ALL_ACCESS, False, self._pid)
        if self._handle is None:
            print(WinError(GetLastError()))
            return 0
        self._last_access = dt.datetime.now()
        return 1

    def read_memory_address(self, address: int, size: int = 1, mem_segment: int = 1) -> bytearray:
        buffer = ct.create_string_buffer(size)
        bytesRead = ct.c_size_t()
        start_addr = self._mem1_addr
        if mem_segment == 2:
            start_addr = self._mem2_addr
        addr = start_addr + address

        result = self.ReadProcessMemory(self._handle, addr, buffer, size, ct.byref(bytesRead))
        error = ct.GetLastError()
        if result:
            self._last_access = dt.datetime.now()
            # print(hex(address), "Success:", buffer)
        else:
            print(hex(address), "Failed.", result, error)

        return bytearray.fromhex(buffer.raw.hex())

    def write_to_memory(self, address: int, value: bytearray, mem_segment: int = 1):
        size = ct.c_size_t(len(value))
        buffer = ct.create_string_buffer(len(value))
        buffer.raw = bytes(value)
        bytesWritten = ct.c_size_t()
        start_addr = self._mem1_addr
        if mem_segment == 2:
            start_addr = self._mem2_addr
        addr = start_addr + address

        result = self.WriteProcessMemory(self._handle, addr, buffer, size, ct.byref(bytesWritten))
        error = ct.GetLastError()
        if result:
            self._last_access = dt.datetime.now()
            # print(hex(address), "Success:", buffer)
        else:
            print(hex(address), "Failed.", result, error)

        return bytearray.fromhex(buffer.raw.hex())

    def _get_dolphin_mems(self):
        MEM1Found = False
        si = SYSTEM_INFO()
        psi = byref(si)
        windll.kernel32.GetSystemInfo(psi)
        base_address = si.lpMinimumApplicationAddress
        max_address = si.lpMaximumApplicationAddress
        page_address = base_address
        m_MEM2Present = False
        self._mem1_addr = 0
        while page_address < max_address:
            info = VirtualQueryEx(self._handle, page_address, False)
            page_address += info.RegionSize
            # Check region size so that we know it's MEM2
            if not m_MEM2Present and info.RegionSize == 0x4000000:
                regionBaseAddress = info.BaseAddress

                if MEM1Found and regionBaseAddress > self._mem1_addr + 0x10000000:
                    # In some cases MEM2 could actually be before MEM1.Once we find MEM1, ignore regions of
                    # this size that are too far away.There apparently are other non-MEM2 regions of size
                    # 0x4000000.
                    break
                # View the comment for MEM1.
                wsInfo, success = QueryWorkingSetEx(self._handle, info.BaseAddress)
                if success:
                    if wsInfo.VirtualAttributes.Valid:
                        self._mem2_addr = regionBaseAddress
                        m_MEM2Present = True

            elif info.RegionSize == 0x2000000 and info.Type == 'MEM_MAPPED':
                # Here, it's likely the right page, but it can happen that multiple pages with these criteria
                # exists and have nothing to do with the emulated memory.Only the right page has valid
                # working set information so an additional check is required that it is backed by physical
                # memory.
                wsInfo, success = QueryWorkingSetEx(self._handle, info.BaseAddress)
                if success:
                    if wsInfo.VirtualAttributes.Valid:
                        if not MEM1Found:
                            self._mem1_addr = info.BaseAddress
                            MEM1Found = True
                        else:
                            aramCandidate = info.BaseAddress
                            if aramCandidate == self._mem1_addr + 0x2000000:
                                m_emuARAMAdressStart = aramCandidate
                                m_ARAMAccessible = True

    def shutdown(self):
        if self._handle is not None:
            self.CloseHandle(self._handle)


if __name__ == '__main__':
    cnt = DolphinMemoryController()
    cnt.attach_to_dolphin()
    cnt.write_to_memory(0x00311ac4, bytearray.fromhex('00000299'))
