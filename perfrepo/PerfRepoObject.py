"""
This module contains the base PerfRepo object - PerfRepoObject.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import xml.dom.minidom
from xml.etree import ElementTree

class PerfRepoObject(object):
    def __init__(self):
        pass

    def get_obj_url(self):
        return "/"

    def _set_element_atrib(self, element, name, value):
        if value != None:
            element.set(name, value)

    def to_xml(self):
        pass

    def to_xml_string(self):
        root = self.to_xml()
        return ElementTree.tostring(root)

    def to_pretty_xml_string(self):
        tmp_xml = xml.dom.minidom.parseString(self.to_xml_string())
        return tmp_xml.toprettyxml()

    def __str__(self):
        return self.to_pretty_xml_string()
