import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_1': [],
    'm_2': ["interface port1.6.1", "description something new", "speed 10000", "duplex full", "shutdown"],
    'm_3': ["interface vlan2", "description something new", "mtu 1000"],
    'm_4': ["interface port1.6.6", "description something different", "speed 10000", "duplex auto", "shutdown"],
    'm_5': ["interface vlan1", "description something different", "mtu 1000"],
    'm_6': [],
    'm_7': ["interface vlan1", "no shutdown"],
    'm_8': ["interface port1.6.6", "shutdown"],
    'm_9': [],
    'm_10': [],
    'm_11': [],
    'm_12': [],
    'm_13': [],
    'm_14': [],
    'm_15': [],
    'm_16': [],
    'r_1': [],
    'r_2': ["interface port1.6.5", "description new description", "speed 10000", "duplex full"],
    'r_3': ["interface vlan1", "no description", "no mtu", "no shutdown", "mtu 1105", "no shutdown"],
    'r_4': ["interface vlan1", "no description", "no mtu", "no shutdown"],
    'r_5': [],
    'r_6': [],
    'o_1': ["interface port1.6.6", "no description", "no speed", "no duplex",
            "interface vlan1", "no description", "no mtu", "no shutdown"],
    'o_2': ["interface port1.6.7", "description new test description", "speed 1000", "duplex auto",
            "interface vlan2", "description new test description", "mtu 100", "shutdown",
            "interface port1.6.6", "no description", "no speed", "no duplex",
            "interface vlan1", "no description", "no mtu", "no shutdown"],
    'o_3': ["interface port1.6.6", "no description", "no speed",
            "no duplex", "description new test description", "duplex auto", "shutdown",
            "interface vlan1", "no description", "no mtu", "no shutdown"],
    'o_4': ["interface port1.6.6", "no description", "no speed", "no duplex",
            "interface vlan1", "no description", "no mtu", "no shutdown"],
    'o_5': [],
    'd_1': [],
    'd_2': ["interface port1.6.6", "no description", "no speed", "no duplex",
            "interface vlan1", "no description", "no mtu", "no shutdown"],
    'd_3': [],
    'd_4': [],
    'd_5': ["interface port1.6.6", "no description", "no speed", "no duplex"],
    'd_6': ["interface vlan1", "no description", "no mtu", "no shutdown"]
}


def run_playbook(playbook, tag, debug=False):
    result = subprocess.run(['ansible-playbook', '-v', f'-t {tag}', f'{pb_dir}/{playbook}'], stdout=subprocess.PIPE)
    if debug:
        print(result.stdout.decode('utf-8'))
    return result.stdout.decode('utf-8')


def parse_output(op, tag='test_init'):
    looking = True

    pop = ""
    for outl in op.splitlines():
        ls = outl.strip()
        if looking:
            if ls.startswith(('ok:', 'changed:')):
                pop = "{"
                looking = False
        else:
            if ls.startswith('changed:'):
                pop += ls
                if outl.rstrip() == '}':
                    break

    pop = pop.replace("false", "False")
    pop = pop.replace("true", "True")
    pop = pop.replace("null", "None")
    pop = pop.replace('{changed: [aw1] => ', '')
    pop = pop.replace('ok: [aw1] => ', '')

    try:
        pop = ast.literal_eval(pop)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return []
    return pop.get('commands')


def check_list(list1, list2, debug=False):
    if debug:
        print(list1, list2)
    return sorted(list1) == sorted(list2)


def run_a_test(test_name, debug=False):
    if test_name not in tests:
        return True
    op = run_playbook('test_awplus_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_switchport_config():
    assert run_a_test('m_2')


def test_merge_new_vlan_config():
    assert run_a_test('m_3')


def test_merge_existing_switchport_config():
    assert run_a_test('m_4')


def test_merge_existing_vlan_config():
    assert run_a_test('m_5')


def test_merge_idempotent_test():
    assert run_a_test('m_6')


def test_merge_shutdown_to_no_shutdown():
    assert run_a_test('m_7')


def test_merge_no_shutdown_to_shutdown():
    assert run_a_test('m_8')


def test_merge_out_of_range_item_1():
    assert run_a_test('m_9')


def test_merge_out_of_range_item_2():
    assert run_a_test('m_10')


def test_merge_out_of_range_item_3():
    assert run_a_test('m_11')


def test_merge_out_of_range_item_4():
    assert run_a_test('m_12')


def test_merge_out_of_range_item_5():
    assert run_a_test('m_13')


def test_merge_incompatible_config_1():
    assert run_a_test('m_14')


def test_merge_incompatible_config_2():
    assert run_a_test('m_15')


def test_merge_incompatible_config_3():
    assert run_a_test('m_16')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_nothing_with_new_config():
    assert run_a_test('r_2')


def test_replace_existing_config():
    assert run_a_test('r_3')


def test_remove_with_replaced():
    assert run_a_test('r_4')


def test_replace_using_non_existing_name():
    assert run_a_test('r_5')


def test_replace_idempotency_test():
    assert run_a_test('r_6')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_with_new_configs():
    assert run_a_test('o_2')


def test_override_existing_configs():
    assert run_a_test('o_3')


def test_override_using_non_existing_name():
    assert run_a_test('o_4')


def test_override_idempotency_test():
    assert run_a_test('o_5')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_configs_using_name():
    assert run_a_test('d_2')


def test_delete_config_in_empty_interface():
    assert run_a_test('d_3')


def test_delete_invalid_interface_name():
    assert run_a_test('d_4')


def test_delete_items_in_switchport_interface():
    assert run_a_test('d_5')


def test_delete_items_in_vlan_interface():
    assert run_a_test('d_6')
