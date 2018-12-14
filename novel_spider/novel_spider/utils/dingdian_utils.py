import re


def get_author(value):
    match_obj = re.match(r'作.*者：(\w+)', value)
    if match_obj:
        return match_obj.group(1)
    return ""


def get_category(value):
    match_obj = re.match(r'.*?>(.*)?>.*', value, re.DOTALL)
    if match_obj:
        return match_obj.group(1).strip()
    else:
        return ""


def get_index(value):
    match_obj = re.match(r'.*?/(\d+).html', value)
    if match_obj:
        return int(match_obj.group(1))
    return 0
