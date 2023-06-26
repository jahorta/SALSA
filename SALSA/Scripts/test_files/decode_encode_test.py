# This file tests decoding and encoding of sct files.

# Requires a script directory to run
script_dir = './../../compressed_scripts'

# Determines whether compressed or decompressed scripts are checked
check_compressed = True

# All files between the first and last file names will be checked.
# If first_file == None, starts at beginning
# If last_file == None, goes till end

first_file = None
# first_file = 'me002a.sct'
last_file = None
# last_file = 'me005a.sct'

# Determines whether files are exported if there is a difference
file_out = True

hex_equivalencies = {
    '00000010': '00000006',
    '00000006': '00000010',
    '00000011': '00000007',
    '00000007': '00000011',
    '00000012': '0000000b',
    '0000000b': '00000012',
    '00000013': '0000000c',
    '0000000c': '00000013',
    '00000014': '0000000d',
    '0000000d': '00000014',
    '00000015': '0000000e',
    '0000000e': '00000015',
    '00000016': '0000000f',
    '0000000f': '00000016',
}


def compare_files(ba_1, ba_2):
    d = {}
    if len(ba_1) != len(ba_2):
        d['length'] = f'Original is {len(ba_1)} bytes long, Encoded is {len(ba_2)} bytes long'
    else:
        for word in range(0, len(ba_1) // 4 + 1):
            original_word = ba_1[word * 4: word * 4 + 4]
            encoded_word = ba_2[word * 4: word * 4 + 4]

            # check that the words are the same
            if original_word.hex() == encoded_word.hex():
                continue

            # check that the endian hasn't changed
            if bytearray(reversed(original_word)).hex() == encoded_word.hex():
                continue

            # check that a different parameter code hasn't been used
            if original_word.hex() in hex_equivalencies:
                if encoded_word.hex() == hex_equivalencies[original_word.hex()]:
                    continue

            d[word * 4] = f'Original is {original_word.hex()}, Encoded has {encoded_word.hex()}'
    return d


def save_diffs(d_dict, path):
    out_str = '"Script Name","Difference Name","Difference"'
    for n, d in d_dict.items():
        for diff_name, diff_str in d.items():
            out_str += f'\n{n},{diff_name},{diff_str}'

    with open(path, 'w') as fh:
        fh.write(out_str)


if __name__ == '__main__':
    import os
    cur_dir = os.path.dirname(__file__)
    os.chdir(os.path.pardir)
    os.chdir(os.path.pardir)
    os.chdir(os.path.pardir)
    from SALSA.FileModels.sct_model import SCTModel
    from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
    from SALSA.Scripts.script_decoder import SCTDecoder
    from SALSA.Scripts.script_encoder import SCTEncoder
    from SALSA.AKLZ.aklz import Aklz
    os.chdir(cur_dir)
    os.chdir(os.path.pardir)

    baseinsts = BaseInstLibFacade()

    sct_model = SCTModel()

    files = os.listdir(script_dir)

    differences = {}
    skip_till = first_file if first_file is not None else 'me002a.sct'
    skip = True
    for f in files:
        if f == skip_till:
            skip = False

        if skip:
            continue

        file_dir = script_dir
        filepath = os.path.join(file_dir, f)
        name, original_ba = sct_model.read_sct_file(filepath=filepath)

        print(f'Starting decode for {f.split(".")[0]}')
        script = SCTDecoder.decode_sct_from_file(f.split('.')[0], sct=original_ba, inst_lib=baseinsts)

        print(f'Starting re-encode for {f.split(".")[0]}')
        encoded_ba = SCTEncoder.encode_sct_file_from_project_script(project_script=script, base_insts=baseinsts,
                                                                    use_garbage=True, combine_footer_links=False,
                                                                    add_spurious_refresh=True, validation=True)
        if check_compressed:
            aklz = Aklz()
            original_ba = aklz.compress(original_ba)
            aklz = Aklz()
            encoded_ba = aklz.compress(encoded_ba)

        diffs = compare_files(original_ba, encoded_ba)
        if len(diffs) != 0:
            differences[name] = diffs

        if name in differences and file_out:
            filepath_enc = f'./test_files/re-encodes/{name}_out.sct'
            filepath_orig = f'./test_files/originals/{name}_out.sct'
            sct_model.save_sct_file(filepath=filepath_enc, sct_file=encoded_ba, compress=check_compressed)
            sct_model.save_sct_file(filepath=filepath_orig, sct_file=original_ba, compress=check_compressed)
            # break

        if f == last_file:
            break

    out_path = f'./test_files/diffs_2.csv'
    save_diffs(differences, out_path)
