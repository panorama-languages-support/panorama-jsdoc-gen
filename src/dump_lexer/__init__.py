import re

class ScopeData:
    def __init__(self) -> None:
        self.fieldnames:list[str] = []
        self.data:list[list[str]] = []
    
    def add_field(self, fieldname: str) -> None:
        self.fieldnames.append(fieldname)

    def add_data(self, data: list[str]) -> None:
        self.data.append(data)

class ComponentData:
    def __init__(self, name: str, data: list[ScopeData]) -> None:
        self.name:str = name
        self.data:list[ScopeData] = data

class PanoramaDumpLexer:
    component_regex = '^==.*==$'
    start_regex = '^\{\|' # usually ends in some CSS styling that we can just ignore
    end_regex = '^\|\}'
    field_regex = '^! ' # denotes a new field declaration
    data_scope_open_regex = '^\|-'
    data_regex = '^\| '
    
    @staticmethod
    def tokenize(lines: list[str]) -> list[ComponentData]:

        component_data:list[ComponentData] = []
        scope_data:list[ScopeData] = []

        cur_component:str = ''
        cur_scope_data:ScopeData = None
        cur_data:list[str] = []

        def push_cur_component_data() -> None:
            if len(scope_data) != 0:
                component_data.append(ComponentData(cur_component, scope_data))

        def push_cur_scope_data() -> None:
            if cur_scope_data is not None and len(cur_data) != 0:
                cur_scope_data.add_data(cur_data)

        for idx, line in enumerate(lines):
            
            # Remove trailing newline if there is one
            line:str = str(line)[:-1] if line[len(line) - 1] == '\n' else str(line)

            if re.search(PanoramaDumpLexer.component_regex, line):
                push_cur_component_data()
                scope_data = []
                cur_component = line.strip('==').strip()

            elif re.search(PanoramaDumpLexer.start_regex, line):
                cur_scope_data = ScopeData()

            elif re.search(PanoramaDumpLexer.end_regex, line):
                push_cur_scope_data()
                scope_data.append(cur_scope_data)
                cur_scope_data = None
                cur_data = []
                
            elif re.search(PanoramaDumpLexer.field_regex, line):
                cur_scope_data.add_field(line.lstrip('! '))

            elif re.search(PanoramaDumpLexer.data_scope_open_regex, line):
                push_cur_scope_data()
                cur_data = []
            
            elif re.search(PanoramaDumpLexer.data_regex, line):
                cur_data.append(line.lstrip('| '))

            # EOF
            # Do last to finish processing anything that might be on last line!
            if (idx == len(lines) - 1):
                push_cur_component_data()

        return component_data
