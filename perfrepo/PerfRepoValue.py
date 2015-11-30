"""
This module contains the PerfRepoValue class.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import textwrap
from types import NoneType, StringType
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, iselement
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.Common import PerfRepoException
from perfrepo.Common import indent

class PerfRepoValue(PerfRepoObject):
    def __init__(self, xml=None):
        if type(xml) is NoneType:
            self._metricComparator = None
            self._metricName = None
            self._result = None
            self._parameters = []
        elif type(xml) is StringType or isinstance(xml, Element):
            if type(xml) is StringType:
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "value":
                raise PerfRepoException("Invalid xml.")

            self._metricComparator = root.get("metricComparator")
            self._metricName = root.get("metricName")
            self._result = float(root.get("result"))

            self._parameters = []
            for param in root.find("parameters"):
                if param.tag != "parameter":
                    continue
                self._parameters.append((param.get("name"), param.get("value")))
        else:
            raise PerfRepoException("Parameter xml must be"\
                                    " a string, an Element or None")

    def set_result(self, result):
        self._result = result

    def set_comparator(self, comparator):
        if comparator not in ["HB", "LB"]:
            raise PerfRepoException("Comparator must be HB/LB.")
        self._metricComparator = comparator

    def set_metricName(self, name):
        self._metricName = name

    def add_parameter(self, name, value):
        self._parameters.append((name, value))

    def get_parameters(self):
        return self._parameters

    def get_metricName(self):
        return self._metricName

    def get_comparator(self):
        return self._metricComparator

    def get_result(self):
        return self._result

    def to_xml(self):
        root = Element('value')
        self._set_element_atrib(root, 'metricComparator',
                                      self._metricComparator)
        self._set_element_atrib(root, 'metricName', self._metricName)
        self._set_element_atrib(root, 'result', str(self._result))

        parameters = ElementTree.SubElement(root, 'parameters')
        for param in self._parameters:
            param_elem = ElementTree.SubElement(parameters, 'parameter')
            self._set_element_atrib(param_elem, "name", param[0])
            self._set_element_atrib(param_elem, "value", param[1])
        return root

    def __str__(self):
        ret_str = """\
                  metric name = %s
                  result = %s
                  """ % ( self._metricName,
                          self._result)
        ret_str = textwrap.dedent(ret_str)
        ret_str += "parameters:\n"
        for param in self._parameters:
            ret_str +=  indent("%s = %s\n" % (param[0], param[1]), 4)
        return textwrap.dedent(ret_str)
