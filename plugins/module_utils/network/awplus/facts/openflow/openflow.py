#
# -*- coding: utf-8 -*-
# Copyright 2021 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The awplus openflow fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.openflow.openflow import OpenflowArgs


class OpenflowFacts(object):
    """ The awplus openflow fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = OpenflowArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    # Needs to be mockable for unit tests.
    @staticmethod
    def get_openflow_conf(connection):
        return connection.get("show openflow config").splitlines()

    # Needs to be mockable for unit tests.
    @staticmethod
    def get_openflow_stat(connection):
        return connection.get("show openflow stat").splitlines()

    # Needs to be mockable for unit tests.
    @staticmethod
    def get_run_openflow(connection):
        return connection.get("show running-config | grep openflow").splitlines()

    def render_controllers(self, goc):
        """
        Get controller configuration
        IN: goc - splitlines output of "show openflow config"
        OUT: list of controller dicts
        """
        seen_controller = False
        c_list = []
        for cl in goc:
            cl = cl.strip()
            if not seen_controller:
                oc = re.match(r'Controller "(tcp|ssl):(\S+):(\d+)"', cl)
                if oc:
                    seen_controller = True
                    oc_dict = dict()
                    oc_dict["protocol"] = oc.group(1)
                    oc_dict["address"] = oc.group(2)
                    oc_dict["l4_port"] = oc.group(3)
            else:
                cn = re.search(r'name=(\S+)[,}]', cl, re.U)
                if cn:
                    seen_controller = False
                    oc_dict["name"] = cn.group(1)
                    c_list.append(oc_dict)
        return c_list

    def render_ports(self, goc):
        """
        Get port configuration
        IN: goc - splitlines output of "show openflow config"
        OUT: list of port dicts
        """
        p_list = []
        for pl in goc:
            pl = pl.strip()
            match = re.search(r'Port (port\S+)', pl)
            if match:
                p_list.append(match.group(1))
        return p_list

    def render_other(self, gro):
        """
        Get other configuration, including DPID, inactivity timer, failure mode
        and native VLAN ID.
        IN: gro - splotlines output of "show running-config | grep openflow"
        OUT: dict of other parameters
        """
        ret = dict()

        # Datapath ID (DPID)
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow datapath-id ([0-9a-fA-F]{16})', line, re.U)
            if match:
                ret['datapath_id'] = match.group(1)
                break

        # Inactivity timer
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow inactivity (\d+)', line, re.U)
            if match:
                ret['inactivity_timer'] = int(match.group(1))
                break

        # Failure mode
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow failmode (.+)', line, re.U)
            if match:
                ret['fail_mode'] = "standalone" if match.group(1) == "standalone" else "secure_nre"
                break

        # Native VLAN
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow native vlan (\d+)', line, re.U)
            if match:
                ret['native_vlan'] = int(match.group(1))
                break

        # Trustpoint
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow ssl trustpoint (.+)', line, re.U)
            if match:
                ret['trustpoint'] = match.group(1)
                break

        # Peer certificate
        for line in gro:
            line = line.strip()
            match = re.search(r'openflow ssl peer certificate (.+)', line, re.U)
            if match:
                ret['peer_certificate'] = match.group(1)
                break

        return ret

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for openflow
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            # Normal situation should be no data. Since we need data
            # from multiple sources, it's probably best if we just ignore
            # any data passed in.
            pass

        # Get required information
        goc = self.get_openflow_conf(connection)
        gro = self.get_run_openflow(connection)

        # split the config into instances of the resource. don't do it the way
        # the template suggests since we can't just conveniently split the data
        # into sections.
        config = deepcopy(self.generated_spec)

        # get list of controllers and ports and add to config.
        config["controllers"] = self.render_controllers(goc)
        config["ports"] = self.render_ports(goc)

        # get all other openflow parameters and add to config
        config.update(self.render_other(gro))

        config = utils.remove_empties(config)

        ansible_facts['ansible_network_resources'].pop('openflow', None)

        # we have all the facts in config, no need to validate
        ##facts = {}
        ##if objs:
        ##    params = utils.validate_config(self.argument_spec, {'config': objs})
        ##    facts['openflow'] = params['config']

        facts = {'openflow': config}
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
