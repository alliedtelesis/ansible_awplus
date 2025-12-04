#
# -*- coding: utf-8 -*-
# Copyright 2023 Allied Telesis
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
Action module class for awplus_user
This is used to automatically inject the current ansible_user into
the args of the awplus_user module so that the user does
not have to specify which user Ansible is using to connect.
"""

import copy
from ansible.plugins.action import ActionBase
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.argspec.user.user import UserArgs
from ansible_collections.alliedtelesis.awplus.plugins.module_utils.network.awplus.config.user.user import User


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        module_args = copy.deepcopy(self._task.args)
        module_args['ansible_user'] = task_vars.get('ansible_user')
        module_return = self._execute_module(
            module_name='alliedtelesis.awplus.awplus_user',
            module_args=module_args,
            task_vars=task_vars,
            tmp=tmp
        )
        return module_return
