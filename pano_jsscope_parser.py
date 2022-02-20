import copy
import re
from enum import Enum

# Parses the output of dump_panorama_js_scopes

class JSScopesParserArguments:
    def __init__(self, filename: str, applyhack: bool=False) -> None:
        self.filename = filename
        self.applyhack = applyhack

class Argument:
    def __init__(self, arg: str) -> None:
        split_string:list[str] = arg.split(' ', 1)
        self.type:str = split_string[0]

        self.name:str = '' if len(split_string) <= 1 else split_string[1].replace(' ', '_')
        self.variadic:bool = self.type == 'js_raw_arg' # special arg that signifies what could be any amount of args

class FuncSignature:
    def __init__(self) -> None:
        self.args:list[Argument] = []
        self.name:str = ''
        self.return_type:str = ''
        self.special_base_type:str = ''

    def __init__(self, sig: str) -> None:
        self.parseSig(sig)
        self.special_base_type:str = ''

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

    def setArgs(self, args: list[str]) -> None:
        self.args = args
    
    def setSpecialBaseType(self, base_type: str) -> None:
        self.special_base_type = base_type

class BaseDataType:
    def __init__(self) -> None:
        self.name:str = '',
        self.desc:str = '',
        self.special_base_type:str = ''
        
    def setName(self, name: str) -> None:
        self.name = name
    def setDesc(self, desc: str) -> None:
        self.desc = desc
    def setSpecialBaseType(self, base_type: str) -> None:
        self.special_base_type = base_type

class PropertyType(BaseDataType):
    def __init__(self) -> None:
        BaseDataType.__init__(self)
        self.type:str = '',
        self.readonly:bool = False,

    def setType(self, type: str) -> None:
        self.type = type
    def setReadonly(self, readonly: bool) -> None:
        self.readonly = readonly

class MethodType(BaseDataType):
    def __init__(self):
        BaseDataType.__init__(self)
        self.sig:FuncSignature = {}

    def setSig(self, sig: FuncSignature) -> None:
        self.sig = sig

class PanoramaPanelData:
    def __init__(self, name: str, is_api: bool, property_data: list[PropertyType], method_data: list[MethodType]) -> None:
        self.name:str = name
        self.is_api:bool = is_api
        self.property_data:list[PropertyType] = property_data
        self.method_data:list[MethodType] = method_data

class JSScopesParser:
    class SCOPE_TYPE(Enum):
        UNKNOWN = 0
        PROPERTY = 1
        METHOD = 2
        
    typename_regex = '^==.*==$'
    api_regex = '\$|API$' # this runs after stripping (on just word)
    scope_open_regex = '^\{\|' # usually ends in some CSS styling that we can just ignore
    scope_close_regex = '^\|\}'
    is_property_regex = '^! (Property Name|Type|ReadOnly)'
    is_method_regex = '^! (Method Name|Signature)'
    data_scope_open_regex = '^\|-'
    data_regex = '^\| '

    @staticmethod
    def parse(args: JSScopesParserArguments) -> list[PanoramaPanelData]:
        panorama_panel_data:list[PanoramaPanelData] = []
        property_data:list[PropertyType] = []
        method_data:list[MethodType] = []
        scope_name:str = ''
        scope_is_api:bool = False
        scope_type:JSScopesParser.SCOPE_TYPE = None
        current_property_data:PropertyType = PropertyType()
        current_method_data:MethodType = MethodType()
        parsed_count:int = 0
        parsed_count_inner:int = 0
        
        def capturePanelData() -> None:
            panel_data = PanoramaPanelData(name=scope_name, is_api=scope_is_api, property_data=copy.deepcopy(property_data), method_data=copy.deepcopy(method_data))
            panorama_panel_data.append(panel_data)
            property_data.clear()
            method_data.clear()

        def captureScope() -> None:
            if (scope_type == JSScopesParser.SCOPE_TYPE.PROPERTY):
                property_data.append(copy.deepcopy(current_property_data))
            elif (scope_type == JSScopesParser.SCOPE_TYPE.METHOD):
                method_data.append(copy.deepcopy(current_method_data))

        def captureScopeInner() -> None:
            if scope_type == JSScopesParser.SCOPE_TYPE.PROPERTY:
                if parsed_count_inner == 0:
                    current_property_data.setName(line)
                elif parsed_count_inner == 1:
                    current_property_data.setType(line)
                elif parsed_count_inner == 2:
                    current_property_data.setReadonly(line == 'X')
                elif parsed_count_inner == 3:
                    current_property_data.setDesc(line)
            elif scope_type == JSScopesParser.SCOPE_TYPE.METHOD:
                if parsed_count_inner == 0:
                    current_method_data.setName(line)
                elif parsed_count_inner == 1:
                    current_method_data.setSig(FuncSignature(sig=line))
                elif parsed_count_inner == 2:
                    current_method_data.setDesc(line)

        with open(args.filename, 'r') as f:

            lines = f.readlines() # list containing lines of file
            for idx, line in enumerate(lines):
                line:str = str(line)[:-1]

                # Make sure we write panel data at eof (since it's written only on new typename)
                if (idx == len(lines) - 1):
                    capturePanelData()
                    continue

                # == Typename ==
                if re.search(JSScopesParser.typename_regex, line):
                    line = line.strip('==').strip()

                    # Starting new type so write the data of the previous type
                    if (scope_type is not None):
                        capturePanelData()

                    scope_name = line
                    scope_is_api = bool(re.search(JSScopesParser.api_regex, line))
                    
                # Entering or leaving a scope, which can either be the property or method defs
                elif re.search(JSScopesParser.scope_open_regex, line):
                    parsed_count = 0
                    parsed_count_inner = 0

                elif re.search(JSScopesParser.scope_close_regex, line):
                    captureScope()
                    parsed_count = 0
                    parsed_count_inner = 0

                elif re.search(JSScopesParser.is_property_regex, line):
                    scope_type = JSScopesParser.SCOPE_TYPE.PROPERTY

                elif re.search(JSScopesParser.is_method_regex, line):
                    scope_type = JSScopesParser.SCOPE_TYPE.METHOD

                # Start of a property or method definition
                elif re.search(JSScopesParser.data_scope_open_regex, line):
                    # Previous scope has ended, add its property/method data
                    if parsed_count > 0:
                        captureScope()
                        parsed_count_inner = 0

                    parsed_count += 1
                
                elif re.search(JSScopesParser.data_regex, line):
                    line = line.lstrip('| ').strip()
                    captureScopeInner()
                    parsed_count_inner += 1
                
                else:
                    pass

        return JSScopesParser.apply_basetype_fixup(panorama_panel_data) if args.applyhack else panorama_panel_data

    ### STUPID HACK ###
    # Special case where the declared function/property has an extra field (namespace.field.blah)
    # Chaos' persistent storage does this
    @staticmethod
    def apply_basetype_fixup(panorama_panel_data:list[PanoramaPanelData]) -> list[PanoramaPanelData]:
        for panel_data in panorama_panel_data:
            if (panel_data.name != '$'):
                continue

            for method in panel_data.method_data:
                if method.desc == '':
                    continue

                func_regex = '^\$..*%s\(.*\)'%method.name
                if not re.search(func_regex, method.desc):
                    continue # Definitely not a function

                func_exact_regex = '^\$.%s\(.*\)'%method.name
                if not re.search(func_exact_regex, method.desc):
                    split_string = method.desc.split('.')
                    method.sig.setSpecialBaseType(split_string[1])

            for property in panel_data.property_data:
                if property.desc == '':
                    continue

                prop_regex = '^\$..*%s'%property.name
                if not re.search(prop_regex, property.desc):
                    continue # Definitely not a property

                prop_exact_regex = '^\$.%s'%property.name
                if not re.search(prop_exact_regex, property.desc):
                    split_string = property.desc.split('.')
                    property.setSpecialBaseType(split_string[1])

        return panorama_panel_data
