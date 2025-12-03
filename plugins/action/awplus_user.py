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
