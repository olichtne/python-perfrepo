"""
This module contains the API for PerfRepo.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import requests
import logging
from perfrepo.PerfRepoObject import PerfRepoObject
from perfrepo.PerfRepoMetric import PerfRepoMetric
from perfrepo.PerfRepoReport import PerfRepoReport
from perfrepo.PerfRepoTest import PerfRepoTest
from perfrepo.PerfRepoTestExecution import PerfRepoTestExecution

class PerfRepoRESTAPI(object):
    '''Wrapper class for the REST API provided by PerfRepo'''
    def __init__(self, url, user, password):
        self._url = url
        self._user = user
        self._password = password

        self._session = requests.Session()
        self._session.auth = (self._user, self._password)
        self._session.stream = True
        self._session.headers['Content-Type'] = 'text/xml'
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_obj_url(self, obj):
        if not isinstance(obj, PerfRepoObject):
            return ""
        return self._url + obj.get_obj_url()

    def test_get_by_id(self, test_id, log=True):
        get_url = self._url + '/rest/test/id/%s' % test_id
        response = self._session.get(get_url)
        if response.status_code != 200:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("GET %s success" % get_url)
            return PerfRepoTest(response.content)

    def test_get_by_uid(self, test_uid, log=True):
        get_url = self._url + '/rest/test/uid/%s' % test_uid
        response = self._session.get(get_url)
        if response.status_code != 200:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("GET %s success" % get_url)
            return PerfRepoTest(response.content)

    def test_create(self, test, log=True):
        post_url = self._url + '/rest/test/create'
        response = self._session.post(post_url, data=test.to_xml_string())
        if response.status_code != 201:
            if log:
                logging.debug(response.text)
            return None
        else:
            new_id = response.headers["Location"].split('/')[-1]
            test.set_id(new_id)
            if log:
                logging.debug("POST %s success" % post_url)
                logging.info("Obj url: %s" % self.get_obj_url(test))
            return test

    def test_add_metric(self, test_id, metric, log=True):
        post_url = self._url + '/rest/test/id/%s/addMetric' % test_id
        response = self._session.post(post_url, data=metric.to_xml_string)
        if response.status_code != 201:
            if log:
                logging.debug(response.text)
            return None
        else:
            new_id = response.headers["Location"].split('/')[-1]
            metric.set_id(new_id)
            if log:
                logging.debug("POST %s success" % post_url)
                logging.info("Obj url: %s" % self.get_obj_url(metric))
            return metric

    def test_delete(self, test_id, log=True):
        delete_url = self._url + '/rest/test/id/%s' % test_id
        response = self._session.delete(delete_url)
        if response.status_code != 204:
            return False
        else:
            if log:
                logging.debug("DELETE %s success" % delete_url)
            return True

    def metric_get(self, metric_id, log=True):
        get_url = self._url + '/rest/metric/%s' % metric_id
        response = self._session.get(get_url)
        if response.status_code != 200:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("GET %s success" % get_url)
            return PerfRepoMetric(response.content)

    def testExecution_get(self, testExec_id, log=True):
        get_url = self._url + '/rest/testExecution/%s' % testExec_id
        response = self._session.get(get_url)
        if response.status_code != 200:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("GET %s success" % get_url)
            return PerfRepoTestExecution(response.content)

    def testExecution_create(self, testExec, log=True):
        post_url = self._url + '/rest/testExecution/create'
        response = self._session.post(post_url, data=testExec.to_xml_string())
        if response.status_code != 201:
            if log:
                logging.debug(response.text)
            return None
        else:
            new_id = response.headers["Location"].split('/')[-1]
            testExec.set_id(new_id)
            if log:
                logging.debug("POST %s success" % post_url)
                logging.info("Obj url: %s" % self.get_obj_url(testExec))
            return testExec

    def testExecution_delete(self, testExec_id, log=True):
        delete_url = self._url + '/rest/testExecution/%s' % testExec_id
        response = self._session.delete(delete_url)
        if response.status_code != 204:
            if log:
                logging.debug(response.text)
            return False
        else:
            if log:
                logging.debug("DELETE %s success" % delete_url)
            return True

    def testExecution_add_value(self, value, log=True):
        post_url = self._url + '/rest/testExecution/addValue'
        #TODO
        return self._session.post(post_url, data=value)

    def testExecution_get_attachment(self, attachment_id, log=True):
        get_url = self._url + '/rest/testExecution/attachment/%s' % \
                                                                attachment_id
        #TODO
        return self._session.get(get_url)

    def testExecution_add_attachment(self, testExec_id, attachment, log=True):
        post_url = self._url + '/rest/testExecution/%s/addAttachment' % \
                                                                testExec_id
        #TODO
        return self._session.post(post_url, data=attachment)

    def report_get_by_id(self, report_id, log=True):
        get_url = self._url + '/rest/report/id/%s' % report_id
        response = self._session.get(get_url)
        if response.status_code != 200:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("GET %s success" % get_url)
            return PerfRepoReport(response.content)

    def report_create(self, report, log=True):
        post_url = self._url + '/rest/report/create'

        report.set_user(self._user)

        response = self._session.post(post_url, data=report.to_xml_string())
        if response.status_code != 201:
            if log:
                logging.debug(response.text)
            return None
        else:
            new_id = response.headers["Location"].split('/')[-1]
            report.set_id(new_id)
            if log:
                logging.debug("POST %s success" % post_url)
                logging.info("Obj url: %s" % self.get_obj_url(report))
            return report

    def report_update(self, report, log=True):
        post_url = self._url + '/rest/report/update/%s' % report.get_id()

        report.set_user(self._user)

        response = self._session.post(post_url, data=report.to_xml_string())
        if response.status_code != 201:
            if log:
                logging.debug(response.text)
            return None
        else:
            if log:
                logging.debug("UPDATE %s success" % post_url)
                logging.info("Obj url: %s" % self.get_obj_url(report))
            return report

    def report_delete_by_id(self, report_id, log=True):
        delete_url = self._url + '/rest/report/id/%s' % report_id
        response = self._session.delete(delete_url)
        if response.status_code != 204:
            return False
        else:
            if log:
                logging.debug("DELETE %s success" % delete_url)
            return True
