import sys
from pano_type_jsdoc import JSDocConverterArgs, JSDocConverter
from util import resource_path

try:
    in_parse_scopes_filename:str = sys.argv[1]
except Exception:
    in_parse_scopes_filename:str = input('JS Scopes dump filename (output of dump_panorama_js_scopes): ')

try:
    in_parse_events_filename:str = sys.argv[2]
except Exception:
    in_parse_events_filename:str = input('JS Events dump filename (output of dump_panorama_events): ')

in_header_filename:str = resource_path('included_files/header_info.js')
in_default_filename:str = resource_path('included_files/js_types_default.js')

jsdoc_converter_args = JSDocConverterArgs(in_parse_scopes_filename, in_parse_events_filename, in_header_filename, in_default_filename)

panorama_jsdoc:list[str] = JSDocConverter.parseAndConvertToJSDoc(args=jsdoc_converter_args)

try:
    out_filename:str = sys.argv[3]
except Exception:
    out_filename:str = input('JSDoc output file: ')
    
jsdoc_file = open(out_filename, 'w')
jsdoc_file.writelines(panorama_jsdoc)
jsdoc_file.close()
