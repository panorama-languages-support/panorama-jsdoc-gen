from pano_jsscope_parser import *

class JSDocConverterArgs:
    def __init__(self, in_header_filename: str, in_default_filename: str) -> None:
        self.in_header_filename = in_header_filename
        self.in_default_filename = in_default_filename

class JSDocConverter:
    @staticmethod
    def parseAndConvertToJSDoc(parser_args: JSScopesParserArguments, args: JSDocConverterArgs) -> list[str]:
        # Run the parser
        panorama_panel_data:list[PanoramaPanelData] = JSScopesParser.parse(parser_args)
   
        # Read header comments first
        header_comments:list[str] = []
        with open(args.in_header_filename, 'r') as f:
            header_comments = f.readlines()
            header_comments.append('\n\n')

        # Read default types before dynamic data
        default_jsdoc:list[str] = []
        if args.in_default_filename != '':
            with open(args.in_default_filename, 'r') as f:
                default_jsdoc = f.readlines()
                default_jsdoc.append('\n\n')

        api_jsdoc:list[str] = []
        gen_types_jsdoc:list[str] = []
        for panel_data in panorama_panel_data:

            # APIs are static globals which we represent here as namespaces
            if panel_data.is_api:
                is_special:bool = panel_data.name == '$'

                # make the namespace for the API
                api_jsdoc.append('/** @namespace */\nlet %s = {}\n'%panel_data.name)

                prop_method_api_data:list[str] = []
                special_base_types:list[str] = []
                
                # $ can have fields so add them
                if is_special:
                    for property in panel_data.property_data:
                        has_special_type:bool = property.special_base_type != ''
                        if has_special_type:
                            special_base_types.append(property.special_base_type)
                        append_type:str = '$.%s'%property.name if not has_special_type else '$.%s.%s'%(property.special_base_type, property.name)
                        
                        read_only:bool = '@readonly' if property.readonly else ''
                        prop_method_api_data.append('{\n/** @type {%s} %s */\nlet %s;\n%s = %s;\n}\n'%(property.type, read_only, property.name, append_type, property.name))


                # make the API functions
                for method in panel_data.method_data:
                    has_special_type:bool = method.sig.special_base_type != ''
                    if has_special_type:
                        special_base_types.append(method.sig.special_base_type)

                    # Create dummy function to force intellisense
                    dummy_var:list[str] = [ 'let %s = function('%method.sig.name ]

                    prop_method_api_data.append(
                        '{\n' # Keep in its own local scope to avoid nameclashes
                        '/**\n * @static\n'
                    )

                    # Omit return type if void
                    if method.sig.return_type != 'void':
                        prop_method_api_data.append(' * @returns {%s}\n'%method.sig.return_type)

                    for idx, arg_type in enumerate(method.sig.args):
                        prop_method_api_data.append(' * @param {%s} %s\n'%(arg_type.type, arg_type.name))
                        dummy_var_arg_name:str = arg_type.name if len(arg_type.name) > 0 else arg_type.type # Fallback to typename if arg isnt named
                        if arg_type.variadic and len(method.sig.args) == 1:
                            dummy_var.append('...')
                        dummy_var.append('%s'%dummy_var_arg_name if idx == len(method.sig.args) - 1 else '%s, '%dummy_var_arg_name)

                    prop_method_api_data.append(' */\n')
                    dummy_var.append(') {}\n')
                    prop_method_api_data += dummy_var

                    # Add dummy function to dummy namespace
                    append_type:str = '%s.%s'%(panel_data.name, method.name) if not has_special_type else '%s.%s.%s'%(panel_data.name, method.sig.special_base_type, method.name)
                    prop_method_api_data.append('%s = %s;\n}\n'%(append_type, method.name))

                # Add any special types as subnamespaces
                special_base_types_unique:set[str] = set(special_base_types)
                for special_base_type in special_base_types_unique:
                    api_jsdoc.append('/** @namespace */\n%s.%s = {}\n'%(panel_data.name, special_base_type))

                api_jsdoc += prop_method_api_data

            else:
                gen_types_jsdoc.append('/** @class */\nfunction %s() {\n'%panel_data.name)

                for property in panel_data.property_data:
                    read_only:bool = '@readonly' if property.readonly else ''
                    gen_types_jsdoc.append('/** @type {%s} %s */\nthis.%s;\n'%(property.type, read_only, property.name))

                for method in panel_data.method_data:
                    dummy_var:list[str] = [ 'this.%s = function('%method.sig.name ]

                    gen_types_jsdoc.append('/**\n')
                    if method.sig.return_type != 'void':
                        gen_types_jsdoc.append(' * @returns {%s}\n'%method.sig.return_type)
                        
                    for idx, arg_type in enumerate(method.sig.args):
                        gen_types_jsdoc.append(' * @param {%s} %s\n'%(arg_type.type, arg_type.name))
                        dummy_var_arg_name:str = arg_type.name if len(arg_type.name) > 0 else arg_type.type # Fallback to typename if arg isnt named
                        if arg_type.variadic and len(method.sig.args) == 1:
                            dummy_var.append('...')
                        dummy_var.append('%s'%dummy_var_arg_name if idx == len(method.sig.args) - 1 else '%s, '%dummy_var_arg_name)

                    gen_types_jsdoc.append(' */\n')
                    dummy_var.append(') {}\n')
                    gen_types_jsdoc += dummy_var
                
                gen_types_jsdoc.append('}\n')

        return header_comments + default_jsdoc + api_jsdoc + gen_types_jsdoc
