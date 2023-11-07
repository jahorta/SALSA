import dataclasses
import threading
from typing import List, Union

from SALSA.GUI.dolphin_link_popup import DolphinLinkPopup
from SALSA.Scripts.script_decoder import SCTDecoder

try:
    from SALSA.SCTDebugger.dolphin_memory_controller import DolphinMemoryController, ptr2addr
except ImportError as e:
    raise ImportError(e)


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


game_titles = {
    'GEAE8P': 'SOAL (US)',
    'GEAP8P': 'SOAL (EU)',
    'GEAJ8P': 'SOAL (JP)'
}

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
        'pSCTStart': 0x00310520,
        'pSCTIndex': 0x00310d40,
        'pSCTPos': 0x00310524,
        'curSCTNum': 0x00315154,
        'curSCTLet': 0x00315158
    },
    # JP version
    'GEAJ8P': {
        'pSCTStart': 0x0030c920,
        'pSCTIndex': 0x0030d140,
        'pSCTPos': 0x0030c924,
        'curSCTNum': 0x00311544,
        'curSCTLet': 0x00311548
    }
}


attach_fail_pid = 'Dolphin is not Running'
attach_fail_mem_block = 'No game is running in Dolphin'
attach_fail_game = 'Wrong game is running'
attach_success = 'Dolphin is running'
update_fail_no_sct = 'Current SCT is not in project'
update_fail_errors = 'Export failed: errors'
update_fail_index_size = 'Update failed: New index is too large'
update_fail_sct_size = 'Update failed: New SCT is too large'
update_fail_no_cur_inst = 'Update failed: Unable to find similar inst'
update_success = 'Update succeeded'
cur_sct_success = 'Current SCT is: '

fail_style = 'warning.TLabel'
success_style = 'success.TLabel'


class DolphinLink:
    log_name = 'DolphinLink'

    def __init__(self, callbacks, tk_parent):
        self.callbacks = callbacks
        self.gamecode = None
        self.addrs: Union[None, SOALAddrs] = None
        self._cont = DolphinMemoryController()
        self.view: Union[None, DolphinLinkPopup] = None
        self.view_callbacks = {
            'attach_controller': self.attach_view, 'attach_dolphin': self.attach_to_dolphin,
            'update_sct': self.update_sct, 'set_cur_inst': self.set_selected_inst_as_current
        }

        self.cur_sct = None
        self.tk_pt = tk_parent

    # Setup methods

    def attach_to_dolphin(self):
        result = self._cont.attach_to_dolphin()
        if result == 1:
            if self.view is not None:
                self.view.set_status(stat_type='dolphin', style=fail_style, status=attach_fail_pid)
                self.view.set_active_button('attach')
        elif result == 2:
            if self.view is not None:
                self.view.set_status(stat_type='dolphin', style=fail_style, status=attach_fail_mem_block)
                self.view.set_active_button('attach')
        elif result == 0:
            game_code = self._get_gamecode()
            if game_code not in addresses.keys():
                if self.view is not None:
                    self.view.set_status(stat_type='dolphin', style=fail_style,
                                         status=attach_fail_game + f': {game_code}')
                    self.view.set_active_button('attach')
                return
            self.gamecode = game_code
            self.addrs = SOALAddrs(**addresses[self.gamecode])
            if self.view is not None:
                self.view.set_status(stat_type='dolphin', style=success_style,
                                     status=attach_success + f': {game_titles[game_code]}')
                self.view.set_active_button('update')
            self.start_cur_sct_updater()
        else:
            raise ValueError(f'Unknown result from attempting to attach to Dolphin {result}')
        return result

    def attach_view(self, view: Union[None, DolphinLinkPopup]):
        self.view = view

    def release_handle(self):
        self._cont.shutdown()

    # Dolphin update methods

    def update_sct(self):
        if self.gamecode is None:
            return
        sct_name = self._get_sct_name()
        if not self.callbacks['check_for_script'](sct_name):
            game_code = self._get_gamecode()
            if game_code not in addresses:
                return self.attach_to_dolphin()
            return self.view.set_status(stat_type='update', style=fail_style,
                                        status=update_fail_no_sct + f' {sct_name}')
        self.cur_sct = sct_name
        self.callbacks['update_sct'](sct_name)

    def write_sct_to_dolphin(self, result):
        if isinstance(result, str):
            return self.view.set_status(stat_type='update', style=fail_style,
                                        status=update_fail_errors + f' {result}')
        new_ind, new_sct = result
        index_size = self._get_index_buf_size()
        sct_size = self._get_sct_buf_size()
        if index_size < len(new_ind):
            return self.view.set_status(stat_type='update', style=fail_style,
                                        status=update_fail_index_size + f'{len(new_ind) - index_size} bytes over')
        if sct_size < len(new_sct):
            return self.view.set_status(stat_type='update', style=fail_style,
                                        status=update_fail_sct_size + f'{len(new_sct) - sct_size} bytes over')
        new_inst_offset = self._get_offset_of_similar_inst()
        if new_inst_offset is None or not isinstance(new_inst_offset, int):
            return self.view.set_status(stat_type='update', style=fail_style,
                                        status=update_fail_no_cur_inst + f'{len(new_sct) - sct_size} bytes over')

        new_inst_offset += int.from_bytes(self._read_addr(ba=self.addrs.pSCTStart, ptr_only=True), byteorder='big')
        new_inst_offset = new_inst_offset.to_bytes(length=4, byteorder='big', signed=False)

        self._write_to_addr(value=new_ind, ba=self.addrs.pSCTIndex)
        self._write_to_addr(value=new_sct, ba=self.addrs.pSCTStart)
        self._write_to_addr(value=new_inst_offset, ba=self.addrs.pSCTPos, ptr_only=True)
        self.view.set_status(stat_type='update', status=update_success, style=success_style)

    def set_selected_inst_as_current(self):
        pass

    def start_cur_sct_updater(self):
        sct_updater = threading.Thread(target=self.threaded_cur_sect_updater)
        sct_updater.start()

    def threaded_cur_sect_updater(self):
        game_code = self._get_gamecode()
        if game_code not in addresses:
            if self.view is not None:
                self.view.set_status('cur_sct', status='', style=success_style)
            return self.attach_to_dolphin()
        cur_sct = self._get_sct_name()
        if self.view is not None:
            self.view.set_status('cur_sct', status=cur_sct_success + cur_sct, style=success_style)
        self.tk_pt.after(1000, self.threaded_cur_sect_updater)

    def _get_gamecode(self):
        gamecode = self._cont.read_memory_address(0, 6)
        return gamecode.decode(errors='ignore')

    def get_cur_index(self):
        return self._read_addr(self.addrs.pSCTIndex)

    def get_cur_sct(self):
        return self._read_addr(self.addrs.pSCTStart)

    def _get_index_buf_size(self):
        return self._get_addr_size(self.addrs.pSCTIndex, cur_ptr=self._get_ptr_value_as_addr(self.addrs.pSCTIndex))

    def _get_sct_buf_size(self):
        return self._get_addr_size(self.addrs.pSCTStart, cur_ptr=self._get_ptr_value_as_addr(self.addrs.pSCTStart))

    def _get_sct_name(self):
        sct_num = int.from_bytes(self._read_addr(self.addrs.curSCTNum), byteorder='big')
        sct_let = self._read_addr(self.addrs.curSCTLet).decode()
        return f'me{sct_num:03d}{sct_let}'

    def _get_offset_of_similar_inst(self):
        cur_ind = self.get_cur_index()
        cur_sct_ptr = int.from_bytes(self._read_addr(self.addrs.pSCTStart, ptr_only=True), byteorder='big')
        cur_inst_ptr = int.from_bytes(self._read_addr(self.addrs.pSCTPos, ptr_only=True), byteorder='big')
        cur_inst_offset = cur_inst_ptr - cur_sct_ptr
        if cur_inst_offset < 0:
            self.attach_to_dolphin()
            raise ValueError(f'{self.log_name}: Current inst offset is negative. '
                             f'This should not happen, reattaching to dolphin')

        index = SCTDecoder.generate_index(cur_ind)
        prev_offset = 0
        cur_offset = 0
        for offset in index:
            cur_offset = offset
            if cur_inst_offset < offset:
                break
            prev_offset = offset
        sect_name = index[prev_offset]
        sect_offset = prev_offset
        sect_size = cur_offset - prev_offset

        if not self.callbacks['sect_name_is_used'](self.cur_sct, sect_name, code_only=True):
            return None

        cur_sct_addr = cur_sct_ptr - 0x80000000
        sect_bytes = self._cont.read_memory_address(sect_offset + cur_sct_addr, sect_size)
        decoded_section = SCTDecoder.decode_section_from_bytes(sect_name, sect_bytes, sect_offset,
                                                               self.callbacks['get_inst_lib']())
        desired_inst_offset = self.callbacks['find_similar_inst'](self.cur_sct, decoded_section,
                                                                  cur_inst_offset - sect_offset)
        return desired_inst_offset

    def _get_ptr_value_as_addr(self, ba: BaseAddr):
        if not ba.is_pointer:
            return ba.start_addr
        ptr_value = self._cont.read_memory_address(ba.start_addr, 4)
        addr = int.from_bytes(ptr2addr(ptr_value), byteorder='big')
        return addr

    def _read_addr(self, ba: BaseAddr, ptr_only=False):
        if ptr_only:
            cur_ptr = ba.start_addr
            size = 4
        else:
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

    def _write_to_addr(self, value, ba: BaseAddr, ptr_only=False):
        if ptr_only:
            addr = ba.start_addr
        else:
            addr = self._get_ptr_value_as_addr(ba)
        return self._cont.write_to_memory(addr, value)

    def test_SOAL(self):
        print(f'Current SCT: {self._get_sct_name()}')
        print(f'Index size: {self._get_index_buf_size()}')
        print(f'SCT size: {self._get_sct_buf_size()}')


if __name__ == '__main__':
    dbg = DolphinLink(None, None)
    attached = dbg.attach_to_dolphin()
    if attached != 0:
        print('Dolphin was not attached')
        exit()
    dbg.test_SOAL()
