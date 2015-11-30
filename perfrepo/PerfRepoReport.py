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
import re
import pprint
from types import NoneType, StringType
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.Common import PerfRepoException
from perfrepo.Common import indent, dot_to_dict, recursive_dict_update
from perfrepo.Common import dict_to_dot

class PerfRepoReport(PerfRepoObject):
    def __init__(self, xml=None):
        self._user = None
        if type(xml) is NoneType:
            self._id = None
            self._name = None
            self._type = None
            self._properties = {}
        elif type(xml) is StringType or isinstance(xml, Element):
            if type(xml) is StringType:
                root = ElementTree.fromstring(xml)
            else:
                root = xml
            if root.tag != "report":
                raise PerfRepoException("Invalid xml.")

            self._id = root.get("id")
            self._name = root.get("name")
            self._type = root.get("type")
            self._properties = {}
            for entry in root.find("properties"):
                if entry.tag != "entry":
                    continue
                key_tag = entry.find("key")
                value_tag = entry.find("value")
                tmp_dict = dot_to_dict(value_tag.get("name"),
                                       value_tag.get("value"))
                recursive_dict_update(self._properties, tmp_dict)
        else:
            raise PerfRepoException("Parameter xml must be"\
                                    " a string, an Element or None")

    def get_obj_url(self):
        return "/reports/%s/%s" % (self._type.lower(), self._id)

    def _find_max_num(self, str_tmp, search_dict):
        max_num = -1
        for key, item in search_dict.items():
            match = re.match(r'%s(\d)+' % str_tmp, key)
            if match == None:
                continue
            num = int(match.group(1))

            if num > max_num:
                max_num = num
        return max_num

    def get_chart(self, chart_num):
        chart_name = "chart%d" % chart_num
        for key, chart in self._properties.items():
            if key == chart_name:
                return chart
        return None

    def add_chart(self, name, test_id):
        max_chart_num = self._find_max_num("chart", self._properties)

        chart_name = "chart%d" % (max_chart_num + 1)

        new_chart = self._properties[chart_name] = {}
        new_chart["name"] = str(name)
        new_chart["test"] = str(test_id)

        return new_chart

    def del_chart(self, chart_num):
        chart_name = "chart%d" % chart_num

        if chart_name in self._properties:
            chart = self._properties[chart_name]
            del self._properties[chart_name]
            return chart
        else:
            return None

    def set_chart_name(self, chart_num, name):
        chart = self.get_chart(chart_num)

        if chart:
            chart["name"] = name
            return chart
        else:
            return None

    def set_chart_test_id(self, chart_num, test_id):
        chart = self.get_chart(chart_num)

        if chart:
            chart["test"] = test_id
            return chart
        else:
            return None

    def get_baseline(self, chart_num=0, index=-1):
        chart = self.get_chart(chart_num)

        if chart is None:
            return None

        if index >= 0:
            baseline_name = "baseline%d" % (index)
            for key, item in chart.items():
                if key == baseline_name:
                    return item
            return None
        else:
            baselines = []
            for key, item in chart.items():
                if re.match(r'baseline\d+', key):
                    baselines.append(item)
            if abs(index) <= len(baselines):
                return baselines[index]
            else:
                return None

    def add_baseline(self, chart_num, name, exec_id, metric_id):
        if chart_num is None:
            chart_num = self._find_max_num("chart", self._properties)

        chart = self.get_chart(chart_num)
        if chart is None:
            return None

        max_baseline_num = self._find_max_num("baseline", chart)

        baseline_name = "baseline%d" % (max_baseline_num + 1)

        new_baseline = chart[baseline_name] = {}
        new_baseline["name"] = str(name)
        new_baseline["metric"] = str(metric_id)
        new_baseline["execId"] = str(exec_id)

        return new_baseline

    def del_baseline(self, chart_num, baseline_num):
        chart = self.get_chart(chart_num)
        if chart is None:
            return None

        baseline_name = "baseline%d" % (baseline_num)

        if baseline_name in chart:
            baseline = chart[baseline_name]
            del chart[baseline_name]
            return baseline
        else:
            return None

    def set_baseline_name(self, chart_num, baseline_num, name):
        baseline = self.get_baseline(chart_num, baseline_num)

        if baseline is None:
            return None

        baseline["name"] = name
        return baseline

    def set_baseline_metric(self, chart_num, baseline_num, metric_id):
        baseline = self.get_baseline(chart_num, baseline_num)

        if baseline is None:
            return None

        baseline["metric"] = metric_id
        return baseline

    def set_baseline_execid(self, chart_num, baseline_num, exec_id):
        baseline = self.get_baseline(chart_num, baseline_num)

        if baseline is None:
            return None

        baseline["execId"] = exec_id
        return baseline

    def add_series(self, chart_num, name, metric_id, tags=[]):
        if chart_num is None:
            chart_num = self._find_max_num("chart", self._properties)

        chart = self.get_chart(chart_num)
        if chart is None:
            return None

        max_series_num = self._find_max_num("series", chart)

        series_name = "series%d" % (max_series_num + 1)

        new_series = chart[series_name] = {}
        new_series["name"] = name
        new_series["metric"] = metric_id
        new_series["tags"] = " ".join(tags)

        return new_series

    def get_series(self, chart_num, series_num):
        chart = self.get_chart(chart_num)
        if chart is None:
            return None

        series_name = "series%d" % int(series_num)
        for key, item in chart.items():
            if key == series_name:
                return item
        return None

    def del_series(self, chart_num, series_num):
        if chart_num is None:
            chart_num = self._find_max_num("chart", self._properties)

        chart = self.get_chart(chart_num)
        if chart is None:
            return None

        series_name = "series%d" % (series_num)

        if series_name in chart:
            series = chart[series_name]
            del chart[series_name]
            return series
        else:
            return None

    def set_series_name(self, chart_num, series_num, name):
        series = self.get_series(chart_num, series_num)

        if series is None:
            return None

        series["name"] = name
        return series

    def set_series_metric(self, chart_num, series_num, metric_id):
        series = self.get_series(chart_num, series_num)

        if series is None:
            return None

        series["metric"] = metric_id
        return series

    def set_series_tags(self, chart_num, series_num, tags):
        series = self.get_series(chart_num, series_num)

        if series is None:
            return None

        series["tags"] = " ".join(tags)
        return series

    def remove_series_tags(self, chart_num, series_num, remove_tags):
        series = self.get_series(chart_num, series_num)

        if series is None:
            return None

        tags = series["tags"].split(" ")

        for tag in remove_tags:
            for i in range(tags.count(tag)):
                tags.remove(tag)

        series["tags"] = " ".join(tags)
        return series

    def add_series_tags(self, chart_num, series_num, add_tags):
        series = self.get_series(chart_num, series_num)

        if series is None:
            return None

        tags = series["tags"].split(" ")

        for tag in add_tags:
            if tags.count(tag) == 0:
                tags.append(tag)

        series["tags"] = " ".join(tags)
        return series

    def set_id(self, new_id=None):
        self._id = new_id

    def get_id(self):
        return self._id

    def set_name(self, new_name=None):
        self._name = new_name

    def get_name(self):
        return self._name

    def set_type(self, new_type=None):
        self._type = new_type

    def get_type(self):
        return self._type

    def set_user(self, new_user=None):
        self._user = new_user

    def get_user(self):
        return self._user

    def to_xml(self):
        root = Element('report')
        self._set_element_atrib(root, 'id', self._id)
        self._set_element_atrib(root, 'name', self._name)
        self._set_element_atrib(root, 'type', self._type)
        self._set_element_atrib(root, 'user', self._user)

        properties = ElementTree.SubElement(root, 'properties')
        dot_props = dict_to_dot(self._properties)
        for prop in dot_props:
            entry_elem = ElementTree.SubElement(properties, 'entry')
            key_elem = ElementTree.SubElement(entry_elem, 'key')
            value_elem = ElementTree.SubElement(entry_elem, 'value')

            key_elem.text = prop[0]
            self._set_element_atrib(value_elem, 'name', prop[0])
            self._set_element_atrib(value_elem, 'value', prop[1])

        return root

    def __str__(self):
        str_props = pprint.pformat(self._properties)
        ret_str = """\
                  id = %s
                  name = %s
                  type = %s
                  properties =
                  """ % ( self._id,
                          self._name,
                          self._type)
        ret_str = textwrap.dedent(ret_str)
        ret_str += str_props
        return textwrap.dedent(ret_str)
