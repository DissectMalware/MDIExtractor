import sys
import base64
import re
import json
from XLMMacroDeobfuscator.deobfuscator import process_file

dridex_file = sys.argv[1]

print('[Discovering Starting Point]')
result = process_file(file=dridex_file,
            noninteractive= True,
            noindent= True,
            extract_formula_format='[[CELL-ADDR]]',
            return_deobfuscated= True,
            extract_only= True,
            sort_formulas = True,
            silent= True,
            timeout= 30)

if len(result) > 1:
    sheet = result[0].replace('SHEET:','').split(',')[0].strip()
    start_addr = "'{}'!{}".format(sheet, result[1])

    print("[Start Point]: {}".format(start_addr))

    json_output_path = dridex_file+'.json'
    print('[Emulating XLM macro]')
    result = process_file(file=dridex_file,
                          noninteractive=True,
                          noindent=True,
                          output_formula_format='[[CELL-ADDR]], [[INT-FORMULA]]',
                          return_deobfuscated=True,
                          export_json=json_output_path,
                          start_point=start_addr,
                          silent=True,
                          timeout=30)
    print('[dumped JSON file]: {}'.format(json_output_path))

    with open(json_output_path, 'r') as json_output:
        result = json.load(json_output)
        file_content = base64.b64decode(result['files'][0]['content_base64']).decode('utf_8')
        regex_array = 'Array\((.*)\)'
        array = re.compile(regex_array)
        match = array.search(file_content)
        if(match):
            encoded_urls = match.group(1)
            python_code = encoded_urls.replace('Chr', 'chr').replace('&', '+')
            urls = eval(python_code)
            print('\r\n'.join(urls))

