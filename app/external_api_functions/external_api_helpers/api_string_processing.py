from typing import List
def cache_sys_inst_str_proc(str_list: List[str]):
    quoted_inst = [(f"'{item}'") for item in str_list if item]
    seperator = '\n'
    return seperator.join(quoted_inst)
    