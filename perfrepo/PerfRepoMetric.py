"""
This module contains the PerfRepoMetric class.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import textwrap
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, iselement
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.Common import PerfRepoException
from perfrepo.Common import indent

class PerfRepoMetric(PerfRepoObject):
    def __init__(self, xml=None):
        if xml is None:
            self._id = None
            self._name = None
            self._description = ""
            self._comparator = None
        elif isinstance(xml, str) or isinstance(xml, bytes) or iselement(xml):
            if isinstance(xml, str) or isinstance(xml, bytes):
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "metric":
                raise PerfRepoException("Invalid xml.")

            self._id = root.get("id")
            self._name = root.get("name")
            self._comparator = root.get("comparator")
            if root.find("description") is not None:
                self._description = root.find("description").text
            else:
                self._description = ""
        else:
            raise PerfRepoException("Parameter xml must be"\
                                    " a string, an Element or None")

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_comparator(self):
        return self._comparator

    def set_id(self, id):
        self._id = id

    def set_name(self, name):
        self._name = name

    def set_description(self, description):
        self._description = description

    def set_comparator(self, comparator):
        if comparator not in ["HB", "LB"]:
            raise PerfRepoException("Invalid comparator value.")
        self._comparator = comparator

    def to_xml(self):
        root = Element('metric')
        self._set_element_atrib(root, 'id', self._id)
        self._set_element_atrib(root, 'name', self._name)
        description = ElementTree.SubElement(root, 'description')
        description.text = self._description
        self._set_element_atrib(root, 'comparator', self._comparator)

        return root

    def __str__(self):
        ret_str = """\
                  id = %s
                  name = %s
                  comparator = %s
                  description:
                  """ % ( self._id,
                          self._name,
                          self._comparator)
        ret_str = textwrap.dedent(ret_str)
        ret_str += indent(self._description + "\n", 4)
        return ret_str
