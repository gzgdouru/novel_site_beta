import re


def get_index_by_chapter(value):
    match_obj = re.match(r'.*?/(\d+).html', value)
    if match_obj:
        return int(match_obj.group(1))
    return 0
