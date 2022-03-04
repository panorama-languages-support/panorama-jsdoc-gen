import re
from dump_lexer import *

# Parses the output of dump_panorama_js_scopes

class Argument:
    def __init__(self, arg: str) -> None:
        split_string:list[str] = arg.split(' ', 1)
        self.type:str = split_string[0]

        self.name:str = '' if len(split_string) <= 1 else split_string[1].replace(' ', '_')
        self.variadic:bool = self.type == 'js_raw_arg' # special arg that signifies what could be any amount of args

class FuncSignature:
    def __init__(self, sig: str, special_base_type: str) -> None:
        self.parseSig(sig)
        self.special_base_type:str = special_base_type

    def parseSig(self, sig: str) -> None:
        split_string:list[str] = sig.split(' ', 1)
        self.return_type:str = split_string[0]

        split_string = split_string[1].split('.') # remove type.
        split_string = split_string[1].split('(', 1)
        self.name:str = split_string[0]

        args_string:str = split_string[1].rstrip(')')
        self.args:list[Argument] = []
        if len(args_string) <= 0:
            return

        split_string = args_string.split(',')
        for arg_string in split_string:
            self.args.append(Argument(arg_string.strip()))

class BaseDataType:
    def __init__(self, name: str, desc: str, special_base_type: str) -> None:
        self.name:str = name
        self.desc:str = desc
        self.special_base_type:str = special_base_type

class PropertyType(BaseDataType):
    def __init__(self, name: str, type: str, readonly: bool, desc: str, special_base_type: str) -> None:
        super().__init__(name, desc, special_base_type)
        self.type:str = type
        self.readonly:bool = readonly

class MethodType(BaseDataType):
    def __init__(self, name: str, sig: FuncSignature, desc: str, special_base_type: str):
        super().__init__(name, desc, special_base_type)
        self.sig:FuncSignature = sig

class PanoramaComponentData:
    def __init__(self, name: str, is_api: bool, property_data: list[PropertyType], method_data: list[MethodType]) -> None:
        self.name:str = name
        self.is_api:bool = is_api
        self.property_data:list[PropertyType] = property_data
        self.method_data:list[MethodType] = method_data

class JSScopesParser:
    api_regex = '\$|API$' # this runs after stripping (on just word)

    @staticmethod
    def parse(lines: list[str], applyhack: bool=False) -> list[PanoramaComponentData]:

        pano_component_data:list[PanoramaComponentData] = []

        ### STUPID HACK ###
        # Special case where the declared function/property has an extra field (namespace.field.blah)
        # Chaos' persistent storage does this
        @staticmethod
        def getSpecialBaseType(is_prop: bool, comp_name: str, name: str, desc: str) -> str:
            if not applyhack:
                return ''

            if comp_name != '$': # only applies to $ currently
                return ''

            if desc == '':
                return ''

            if is_prop:
                prop_regex = '^\$..*%s'%name
                if not re.search(prop_regex, desc):
                    return '' # Definitely not a property

                prop_exact_regex = '^\$.%s'%name
                if not re.search(prop_exact_regex, desc):
                    split_string:list[str] = desc.split('.')
                    return split_string[1]

            # just assume it is a method at this point (would fail asserts otherwise)
            else:
                func_regex = '^\$..*%s\(.*\)'%name
                if not re.search(func_regex, desc):
                    return '' # Definitely not a function

                func_exact_regex = '^\$.%s\(.*\)'%name
                if not re.search(func_exact_regex, desc):
                    split_string:list[str] = desc.split('.')
                    return split_string[1]

            return ''

        components_data:list[ComponentData] = PanoramaDumpLexer.tokenize(lines)
        for component_data in components_data:

            property_data:list[PropertyType] = []
            method_data:list[MethodType] = []

            for scope_data in component_data.data:
                is_property:bool = scope_data.fieldnames[0] == 'Property Name'
                is_method:bool = scope_data.fieldnames[0] == 'Method Name'
                assert is_property or is_method

                if is_property:
                    for scope_prop_data in scope_data.data:
                        assert len(scope_prop_data) == 4
                        special_base_type:str = getSpecialBaseType(True, component_data.name, scope_prop_data[0], scope_prop_data[3])
                        property_data.append(PropertyType(scope_prop_data[0], scope_prop_data[1], scope_prop_data[2] == 'X', scope_prop_data[3], special_base_type))
                elif is_method:
                    for scope_method_data in scope_data.data:
                        assert len(scope_method_data) == 3
                        special_base_type:str = getSpecialBaseType(False, component_data.name, scope_method_data[0], scope_method_data[2])
                        method_data.append(MethodType(scope_method_data[0], FuncSignature(scope_method_data[1], special_base_type), scope_method_data[2], special_base_type))

            is_api:bool = re.search(JSScopesParser.api_regex, component_data.name)
            pano_component_data.append(PanoramaComponentData(component_data.name, is_api, property_data, method_data))
                
        return pano_component_data
