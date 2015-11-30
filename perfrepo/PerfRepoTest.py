"""
This module contains the PerfRepoTest class.

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
from xml.etree.ElementTree import Element
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.PerfRepoMetric import PerfRepoMetric
from perfrepo.Common import PerfRepoException
from perfrepo.Common import indent

class PerfRepoTest(PerfRepoObject):
    def __init__(self, xml=None):
        if type(xml) is NoneType:
            self._id = None
            self._name = None
            self._uid = None
            self._description = None
            self._groupid = None
            self._metrics = []
        elif type(xml) is StringType or isinstance(xml, Element):
            if type(xml) is StringType:
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "test":
                raise PerfRepoException("Invalid xml.")

            self._id = root.get("id")
            self._name = root.get("name")
            self._uid = root.get("uid")
            self._groupid = root.get("groupId")
            self._description = root.find("description").text
            self._metrics = []
            for metric in root.find("metrics"):
                if metric.tag != "metric":
                    continue
                self._metrics.append(PerfRepoMetric(metric))
        else:
            raise PerfRepoException("Parameter xml must be"\
                                    " a string, an Element or None")

    def get_obj_url(self):
        return "/test/%s" % self._id

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_uid(self):
        return self._uid

    def get_description(self):
        return self._description

    def get_groupid(self):
        return self._groupid

    def get_metrics(self):
        return self._metrics

    def set_id(self, id):
        self._id = id

    def set_name(self, name):
        self._name = name

    def set_uid(self, uid):
        self._uid = uid

    def set_description(self, description):
        self._description = description

    def set_groupid(self, groupid):
        self._groupid = groupid

    def add_metric(self, metric):
        if not isinstance(metric, PerfRepoMetric):
            return None
        else:
            self._metrics.append(metric)
            return metric

    def to_xml(self):
        root = Element('test')
        self._set_element_atrib(root, 'id', self._id)
        self._set_element_atrib(root, 'name', self._name)
        self._set_element_atrib(root, 'uid', self._uid)
        self._set_element_atrib(root, 'groupId', self._groupid)
        description = ElementTree.SubElement(root, 'description')
        description.text = self._description
        metrics = ElementTree.SubElement(root, 'metrics')
        for metric in self._metrics:
            metrics.append(metric.to_xml())

        return root

    def __str__(self):
        ret_str = """\
                  id = %s
                  uid = %s
                  name = %s
                  groupid = %s
                  description:
                  """ % (self._id,
                         self._uid,
                         self._name,
                         self._groupid)
        ret_str = textwrap.dedent(ret_str)
        ret_str += indent(self._description + "\n", 4)
        ret_str += "metrics:\n"
        for metric in self._metrics:
            ret_str += indent(str(metric) + "\n", 4)
            ret_str += indent("------------------------\n", 4)
        return textwrap.dedent(ret_str)
