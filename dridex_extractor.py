import sys
import base64
import re
import json
from XLMMacroDeobfuscator.deobfuscator import process_file


def uprint(*objects, sep=' ', end='\n', file=sys.stdout, silent_mode=False):
    if silent_mode:
        return

    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        def f(obj):
            return str(obj).encode(enc, errors='backslashreplace').decode(enc)

        print(*map(f, objects), sep=sep, end=end, file=file)


def main(file_path, silent=False):
    extracted_urls = None
    uprint('[Discovering Starting Point]', silent_mode=silent)
    result = process_file(file=file_path,
                          noninteractive=True,
                          noindent=True,
                          extract_formula_format='[[CELL-ADDR]]',
                          return_deobfuscated=True,
                          extract_only=True,
                          sort_formulas=True,
                          silent=True,
                          timeout=30)

    if len(result) > 1:
        sheet = result[0].replace('SHEET:', '').split(',')[0].strip()
        start_addr = "'{}'!{}".format(sheet, result[1])

        uprint("[Start Point]: {}".format(start_addr), silent_mode=silent)

        json_output_path = file_path + '.json'
        uprint('[Emulating XLM macro]', silent_mode=silent)
        result = process_file(file=file_path,
                              noninteractive=True,
                              noindent=True,
                              output_formula_format='[[CELL-ADDR]], [[INT-FORMULA]]',
                              return_deobfuscated=True,
                              export_json=json_output_path,
                              start_point=start_addr,
                              silent=True,
                              timeout=30)
        uprint('[dumped JSON file]: {}'.format(json_output_path), silent_mode=silent)

        with open(json_output_path, 'r') as json_output:
            result = json.load(json_output)
            file_content = base64.b64decode(result['files'][0]['content_base64']).decode('utf_8')
            regex_array = r'Array\((.*)\)'
            array = re.compile(regex_array)
            match = array.search(file_content)
            if (match):
                encoded_urls = match.group(1)
                python_code = encoded_urls.replace('Chr', 'chr').replace('&', '+')
                extracted_urls = eval(python_code)
                uprint('\r\n'.join(extracted_urls), silent_mode=silent)
    return extracted_urls


if __name__ == "__main__":
    dridex_file = sys.argv[1]
    main(dridex_file)
