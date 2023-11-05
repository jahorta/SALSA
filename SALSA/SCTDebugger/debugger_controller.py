import dataclasses
from typing import List, Union

from SALSA.SCTDebugger.dolphin_memory_controller import DolphinMemoryController, ptr2addr

gamecodes = {
    'GEAE8P': 'Skies of Arcadia Legends (US)',
    'GEAP8P': 'Skies of Arcadia Legends (EU)',
    'GEAJ8P': 'Skies of Arcadia Legends (JP)'
}


sct_buf_size_offset = -0x1c


@dataclasses.dataclass
class BaseAddr:
    start_addr: int
    ptr_offsets: List[int] = dataclasses.field(default_factory=list)
    size: int = 4
    size_offset: Union[None, int] = None
    size_mod: int = 0
    is_pointer: bool = False


class SOALAddrs:
    def __init__(self, pSCTIndex, pSCTStart, pSCTPos, curSCTNum, curSCTLet):
        self.pSCTIndex = BaseAddr(pSCTIndex, size_offset=-0x38, size_mod=-0x40, is_pointer=True)
        self.pSCTStart = BaseAddr(pSCTStart, size_offset=-0x38, size_mod=-0x40, is_pointer=True)
        self.pSCTPos = BaseAddr(pSCTPos, is_pointer=True)
        self.curSCTNum = BaseAddr(curSCTNum)
        self.curSCTLet = BaseAddr(curSCTLet, size=1)


addresses = {
    # US version
    'GEAE8P': {
        'pSCTStart': 0x0030cea0,
        'pSCTIndex': 0x0030d6c0,
        'pSCTPos': 0x0030cea4,
        'curSCTNum': 0x00311ac4,
        'curSCTLet': 0x00311ac8
    },
    # EU version
    'GEAP8P': {
        'pSCTStart': -1,
        'pSCTIndex': -1,
        'pSCTPos': -1,
        'curSCTNum': -1,
        'curSCTLet': -1
    },
    # JP version
    'GEAJ8P': {
        'pSCTStart': -1,
        'pSCTIndex': -1,
        'pSCTPos': -1,
        'curSCTNum': -1,
        'curSCTLet': -1
    }
}


class SCTDebugger:

    def __init__(self):
        self.gamecode = None
        self.addrs: Union[None, SOALAddrs] = None
        self._cont = DolphinMemoryController()

    def attach_to_dolphin(self):
        result = self._cont.attach_to_dolphin()
        if result == 1:
            gamecode_bytes = self._cont.read_memory_address(0, 6)
            self.gamecode = gamecode_bytes.decode()
            self.addrs = SOALAddrs(**addresses[self.gamecode])
        return result

    def get_cur_index(self):
        return self._read_addr(self.addrs.pSCTIndex)

    def get_cur_sct(self):
        return self._read_addr(self.addrs.pSCTStart)

    def get_index_buf_size(self):
        return self._get_addr_size(self.addrs.pSCTIndex, cur_ptr=self._get_ptr_value_as_addr(self.addrs.pSCTIndex))

    def get_sct_buf_size(self):
        return self._get_addr_size(self.addrs.pSCTStart, cur_ptr=self._get_ptr_value_as_addr(self.addrs.pSCTStart))

    def get_sct_name(self):
        sct_num = int.from_bytes(self._read_addr(self.addrs.curSCTNum), byteorder='big')
        sct_let = self._read_addr(self.addrs.curSCTLet).decode()
        return f'me{sct_num:03d}{sct_let}'

    def _get_ptr_value_as_addr(self, ba: BaseAddr):
        if not ba.is_pointer:
            return ba.start_addr
        ptr_value = self._cont.read_memory_address(ba.start_addr, 4)
        addr = int.from_bytes(ptr2addr(ptr_value), byteorder='big')
        return addr

    def _read_addr(self, ba: BaseAddr):
        cur_ptr = self._get_ptr_value_as_addr(ba)
        size = self._get_addr_size(ba, cur_ptr=cur_ptr)
        return self._cont.read_memory_address(cur_ptr, size)

    def _get_addr_size(self, ba: BaseAddr, cur_ptr=None):
        if ba.size_offset is None:
            return ba.size + ba.size_mod
        ptr = ba.start_addr
        if cur_ptr is not None:
            ptr = cur_ptr
        return int.from_bytes(self._cont.read_memory_address(ptr + ba.size_offset, 4), byteorder='big') + ba.size_mod


if __name__ == '__main__':
    dbg = SCTDebugger()
    attached = dbg.attach_to_dolphin()
    if attached != 1:
        print('Dolphin was not attached')
        exit()
    print(f'Current SCT: {dbg.get_sct_name()}')
    print(f'Index size: {dbg.get_index_buf_size()}')
    print(f'SCT size: {dbg.get_sct_buf_size()}')
