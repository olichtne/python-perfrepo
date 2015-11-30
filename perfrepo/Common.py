"""
This module contains common functions for Python Perfrepo

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import re
import collections

class PerfRepoException(Exception):
    pass

def bool_it(val):
    if isinstance(val, str):
        if re.match("^\s*(?i)(true)", val) or re.match("^\s*(?i)(yes)", val):
            return True
        elif re.match("^\s*(?i)(false)", val) or re.match("^\s*(?i)(no)", val):
            return False
    return True if int(val) else False

def recursive_dict_update(original, update):
    for key, value in update.iteritems():
        if isinstance(value, collections.Mapping):
            r = recursive_dict_update(original.get(key, {}), value)
            original[key] = r
        else:
            original[key] = update[key]
    return original

def dot_to_dict(name, value):
    result = {}
    last = result
    last_key = None
    previous = None
    for key in name.split('.'):
        last[key] = {}
        previous = last
        last = last[key]
        last_key = key
    if last_key != None:
        previous[last_key] = value
    return result

def list_to_dot(original_list, prefix="", key=""):
    return_list = []
    index = 0
    for value in original_list:
        iter_key = prefix + key + str(index)
        index += 1
        if isinstance(value, collections.Mapping):
            sub_list = dict_to_dot(value, iter_key + '.')
            return_list.extend(sub_list)
        elif isinstance(value, list):
            raise Exception("Nested lists not allowed")
        elif isinstance(value, tuple):
            #TODO temporary fix, tuples shouldn't be here
            if len(value) == 2:
                return_list.append((iter_key+'.'+value[0], value[1]))
        else:
            return_list.append((iter_key, value))
    return return_list

def dict_to_dot(original_dict, prefix=""):
    return_list = []
    for key, value in original_dict.iteritems():
        if isinstance(value, collections.Mapping):
            sub_list = dict_to_dot(value, prefix + key + '.')
            return_list.extend(sub_list)
        elif isinstance(value, list):
            sub_list = list_to_dot(value, prefix, key)
            return_list.extend(sub_list)
        elif isinstance(value, tuple):
            #TODO temporary fix, tuples shouldn't be here
            if len(value) == 2:
                return_list.append((prefix+key,
                                    "(%s, %s)" % (value[0],
                                                  value[1]) ))
        else:
            return_list.append((prefix+key, str(value)))
    return return_list

def indent(string, spaces):
    ret_str = []
    for line in string.split('\n'):
        if line == "":
            ret_str.append(line)
        else:
            ret_str.append(' '*spaces + line)
    return '\n'.join(ret_str)
