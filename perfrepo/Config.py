"""
Module containing class used for loading config files.

Copyright 2015 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__autor__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import os
import sys
import re
from ConfigParser import ConfigParser
from perfrepo.Common import bool_it

class ConfigError(Exception):
    pass

class Config():
    options = None
    _scheme = None

    def __init__(self):
        self._options = dict()

    def opts_init(self):
        self._options['perfrepo'] = dict()
        self._options['perfrepo']['url'] = {\
                "value" : "",
                "additive" : False,
                "action" : self.optionPlain,
                "name" : "url"}
        self._options['perfrepo']['username'] = {\
                "value" : "",
                "additive" : False,
                "action" : self.optionPlain,
                "name" : "username"}
        self._options['perfrepo']['password'] = {\
                "value" : "",
                "additive" : False,
                "action" : self.optionPlain,
                "name" : "password"}

    def get_config(self):
        return self._options

    def get_section(self, section):
        if section not in self._options:
            msg = 'Unknow section: %s' % section
            raise ConfigError(msg)
        return self._options[section]

    def get_option(self, section, option):
        sect = self.get_section(section)
        if option not in sect:
            msg = 'Unknown option: %s in section: %s' % (option, section)
            raise ConfigError(msg)
        return sect[option]["value"]

    def set_option(self, section, option, value):
        sect = self.get_section(section)
        sect[option]["value"] = value

    def load_config(self, path):
        '''Parse and load the config file'''
        exp_path = os.path.expanduser(path)
        abs_path = os.path.abspath(exp_path)
        parser = ConfigParser(dict_type=dict)
        print >> sys.stderr, "Loading config file '%s'" % abs_path
        parser.read(abs_path)

        sections = parser._sections

        self.handleSections(sections, abs_path)

    def handleSections(self, sections, path):
        for section in sections:
            if section in self._options:
                self.handleOptions(section, sections[section], path)
            else:
                msg = "Unknown section: %s" % section
                raise ConfigError(msg)

    def handleOptions(self, section_name, config, cfg_path):
        section = self._options[section_name]

        config.pop('__name__', None)
        for opt in config:
            if not config[opt]:
                continue
            option = self._find_option_by_name(section, opt)
            if option != None:
                if option[1]: #additive?
                    option[0]["value"] +=\
                            option[0]["action"](config[opt], cfg_path)
                else:
                    option[0]["value"] =\
                            option[0]["action"](config[opt], cfg_path)
            else:
                msg = "Unknown option: %s in section %s" % (opt, section_name)
                raise ConfigError(msg)

    def _find_option_by_name(self, section, opt_name):
        match = re.match(r'^(\w*)(\s+\+)$', opt_name)
        if match != None:
            additive = True
            opt_name = match.groups()[0]
        else:
            additive = False

        for option in section.itervalues():
            if option["name"] == opt_name:
                if (not option["additive"]) and additive:
                    msg = "Operator += cannot be used in option %s" % opt_name
                    raise ConfigError(msg)
                return (option, additive)

        return None

    def optionPort(self, option, cfg_path):
        try:
            int(option)
        except ValueError:
            msg = "Option port expects a number."
            raise ConfigError(msg)
        return int(option)

    def optionPath(self, option, cfg_path):
        exp_path = os.path.expanduser(option)
        abs_path = os.path.join(os.path.dirname(cfg_path), exp_path)
        norm_path = os.path.normpath(abs_path)
        return norm_path

    def optionDirList(self, option, cfg_path):
        paths = re.split(r'(?<!\\)\s', option)

        dirs = []
        for path in paths:
            if path == '':
                continue
            norm_path = self.optionPath(path, cfg_path)
            dirs.append(norm_path)

        return dirs

    def optionTimeval(self, option, cfg_path):
        timeval_re = "^(([0-9]+)days?)?\s*(([0-9]+)hours?)?\s*" \
                     "(([0-9]+)minutes?)?\s*(([0-9]+)seconds?)?$"
        timeval_match = re.match(timeval_re, option)
        if timeval_match:
            values = timeval_match.groups()
            timeval = 0
            if values[1]:
                timeval += int(values[1])*24*60*60
            if values[3]:
                timeval += int(values[3])*60*60
            if values[5]:
                timeval += int(values[5])*60
            if values[7]:
                timeval += int(values[7])
        else:
            msg = "Incorrect timeval format."
            raise ConfigError(msg)

        return timeval

    def optionColour(self, option, cfg_path):
        colour = option.split()
        if len(colour) != 3:
            msg = "Colour must be specified by 3"\
                    " values (foreground, background, bold)"\
                    " sepparated by whitespace."
            raise ConfigError(msg)

        return colour

    def optionBool(self, option, cfg_path):
        return bool_it(option)

    def optionPlain(self, option, cfg_path):
        return option

    def dump_config(self):
        string = ""
        for section in self._options:
            string += "[%s]\n" % section
            for option in self._options[section]:
                val = self.value_to_string(section, option)
                opt_name = self._options[section][option]["name"]
                string += "%s = %s\n" % (opt_name, val)

        return string

    def value_to_string(self, section, option):
        string = ""
        value = self._options[section][option]["value"]

        if type(value) == list:
            string = " ".join(value)
        else:
            string = str(value)

        return string

#Global object containing configuration, available across modules
#The object is created here but the contents are initialized
#in the main binaries, after that the modules that need the configuration
#just import this object
config = Config()
