"""
This module contains the PerfRepoTestExecution class.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import datetime
import textwrap
from types import NoneType, StringType
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, iselement
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.PerfRepoValue import PerfRepoValue
from perfrepo.PerfRepoTest import PerfRepoTest
from perfrepo.Common import PerfRepoException
from perfrepo.Common import indent

class PerfRepoTestExecution(PerfRepoObject):
    def __init__(self, xml=None):
        if type(xml) is NoneType:
            self._id = None
            self._name = None
            self._started = datetime.datetime.utcnow().isoformat()
            self._testId = None
            self._testUid = None
            self._comment = ""

            self._values = []
            self._tags = []
            self._parameters = []
        elif type(xml) is StringType or iselement(xml):
            if type(xml) is StringType:
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "testExecution":
                raise PerfRepoException("Invalid xml.")

            self._id = root.get("id")
            self._name = root.get("name")
            self._started = root.get("started")
            self._testId = root.get("testId")
            self._testUid = root.get("testUid")
            if root.find("comment") is not None:
                self._comment = root.find("comment").text
            else:
                self._comment = ""

            self._values = []
            for value in root.find("values"):
                if value.tag != "value":
                    continue
                self._values.append(PerfRepoValue(value))

            self._tags = []
            for tag in root.find("tags"):
                if tag.tag != "tag":
                    continue
                self._tags.append(tag.get("name"))

            self._parameters = []
            for param in root.find("parameters"):
                if param.tag != "parameter":
                    continue
                self._parameters.append((param.get("name"), param.get("value")))
        else:
            raise PerfRepoException("Parameter xml must be"\
                                    " a string, an Element or None")

    def get_obj_url(self):
        return "exec/%s" % self._id

    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_started(self, date=None):
        if isinstance(date, NoneType):
            self._started = datetime.datetime.utcnow().isoformat()
        else:
            self._started = date

    def get_started(self):
        return self._started

    def set_testId(self, testId):
        if isinstance(testId, PerfRepoTest):
            self._testId = testId.get_id()
        else:
            self._testId = testId

    def get_testId(self):
        return self._testId

    def set_testUid(self, testUid):
        if isinstance(testUid, PerfRepoTest):
            self._testUid = testUid.get_uid()
        else:
            self._testUid = testUid

    def get_testUid(self):
        return self._testUid

    def set_comment(self, comment):
        self._comment = comment

    def get_comment(self):
        return self._comment

    def add_value(self, value):
        self._values.append(value)

    def get_values(self):
        return self._values

    def get_value(self, metric_name):
        for val in self._values:
            if val.get_metricName() == metric_name:
                return val

    def add_tag(self, tag):
        if tag is None:
            return
        self._tags.append(tag)

    def remove_tag(self, tag):
        if tag in self._tags:
            self._tags.remove(tag)

    def get_tags(self):
        return self._tags

    def add_parameter(self, name, value):
        self._parameters.append((name, value))

    def get_parameters(self):
        return self._parameters

    def to_xml(self):
        root = Element('testExecution')
        self._set_element_atrib(root, 'id', self._id)
        self._set_element_atrib(root, 'name', self._name)
        self._set_element_atrib(root, 'started', self._started)
        self._set_element_atrib(root, 'testId', self._testId)
        self._set_element_atrib(root, 'testUid', self._testUid)
        comment = ElementTree.SubElement(root, 'comment')
        comment.text = self._comment

        parameters = ElementTree.SubElement(root, 'parameters')
        for param in self._parameters:
            param_elem = ElementTree.SubElement(parameters, 'parameter')
            self._set_element_atrib(param_elem, "name", param[0])
            self._set_element_atrib(param_elem, "value", str(param[1]))

        tags = ElementTree.SubElement(root, 'tags')
        for tag in self._tags:
            tag_elem = ElementTree.SubElement(tags, 'tag')
            self._set_element_atrib(tag_elem, "name", str(tag))

        values = ElementTree.SubElement(root, 'values')
        for value in self._values:
            values.append(value.to_xml())

        return root

    def __str__(self):
        ret_str = """\
                  id = %s
                  name = %s
                  date = %s
                  testId = %s
                  testUid = %s
                  comment = %s
                  tags = %s
                  """ % ( self._id,
                          self._name,
                          self._started,
                          self._testId,
                          self._testUid,
                          self._comment,
                          " ".join(self._tags))
        ret_str = textwrap.dedent(ret_str)
        ret_str += "parameters:\n"
        for param in self._parameters:
            ret_str +=  indent("%s = %s\n" % (param[0], param[1]), 4)
        ret_str += "values:\n"
        for val in self._values:
            ret_str +=  indent(str(val) + "\n", 4)
            ret_str +=  indent("------------------------\n", 4)
        return textwrap.dedent(ret_str)

class PerfRepoTestExecutionSearch():
    def __init__(self, xml=None):
        self._ids = None
        self._testUid = None
        self._testname = None
        self._tags = []
        self._parameters = []

        if type(xml) is StringType or iselement(xml):
            if type(xml) is StringType:
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "test-execution-search":
                raise PerfRepoException("Invalid xml.")

            elem_ids = root.find("ids")
            if elem_ids is not None:
                ids=[]
                for id in elem_ids:
                    ids.append(id.text)
                self.set_ids(ids)

            self._testname = root.get("test-name")
            self._testUid = root.get("test-uid")
            elem_tags = root.find("tags")
            if elem_tags is not None and elem_tags.text is not None:
                tags = root.find("tags").text
                self._tags = tags.split()

            params = root.find("parameters")
            for param in params.findall("parameter"):
                pname = param.find("name")
                pvalue = param.find("value")
                self.add_parameter(pname.text, pvalue.text)

    def set_ids(self, ids):
        self._ids = ids

    def get_ids(self):
        return self._ids

    def set_testName(self, testname):
        self._testname = testname

    def get_testName(self):
        return self._testname

    def set_testUid(self, testUid):
        if isinstance(testUid, PerfRepoTest):
            self._testUid = testUid.get_uid()
        else:
            self._testUid = testUid

    def get_testUid(self):
        return self._testUid

    def add_tag(self, tag):
        if tag is None:
            return
        self._tags.append(tag)

    def remove_tag(self, tag):
        if tag is None:
            return
        self._tags.remove(tag)

    def get_tags(self):
        return self._tags

    def add_parameter(self, name, value):
        self._parameters.append((name, value))

    def get_parameters(self):
        return self._parameters

    def to_xml(self):
        root = Element('test-execution-search')

        if self._testname:
            sub = ElementTree.SubElement(root, 'test-name')
            sub.text = self._testname

        if self._ids:
            sub_ids = ElementTree.SubElement(root, 'ids')
            for i in self._ids:
                sub = ElementTree.SubElement(sub_ids, 'id')
                sub.text = str(i)

        if self.get_testUid():
            sub = ElementTree.SubElement(root, 'test-uid')
            sub.text = self._testUid

        parameters = ElementTree.SubElement(root, 'parameters')
        for param in self._parameters:
            param_elem = ElementTree.SubElement(parameters, 'parameter')
            sub = ElementTree.SubElement(param_elem, 'name')
            sub.text = param[0]
            sub = ElementTree.SubElement(param_elem, "value")
            sub.text = str(param[1])

        if len(self._tags):
            tags_str = ""
            for tag in self._tags:
                tags_str += " %s" % str(tag)

            tags = ElementTree.SubElement(root, 'tags')
            tags.text = tags_str

        return ElementTree.tostring(root)
