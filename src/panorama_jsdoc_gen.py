import sys
from scopes_parser import JSScopesParserArguments
from pano_type_jsdoc import JSDocConverterArgs, JSDocConverter
from util import resource_path

try:
    parser_in_filename:str = sys.argv[1]
except Exception:
    parser_in_filename:str = input('JS Scopes dump filename (output of dump_panorama_js_scopes): ')

converter_in_header_filename:str = resource_path('included_files/header_info.js')
converter_in_default_filename:str = resource_path('included_files/js_types_default.js')

parser_args = JSScopesParserArguments(filename=parser_in_filename, applyhack=True)
jsdoc_converter_args = JSDocConverterArgs(in_header_filename=converter_in_header_filename, in_default_filename=converter_in_default_filename)

panorama_jsdoc:list[str] = JSDocConverter.parseAndConvertToJSDoc(parser_args=parser_args, args=jsdoc_converter_args)

try:
    out_filename:str = sys.argv[2]
except Exception:
    out_filename:str = input('JSDoc output file: ')
    
jsdoc_file = open(out_filename, 'w')
jsdoc_file.writelines(panorama_jsdoc)
jsdoc_file.close()
