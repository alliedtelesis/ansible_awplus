import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'o_1': ["vlan database", "no vlan 50", "no vlan 100"],
    'o_2': ["vlan database", "vlan 500 name new_test_vlan state enable", "no vlan 50", "no vlan 100"],
    'o_3': ["vlan database", "no vlan 50", "vlan 50 name new_name state disable", "no vlan 100"],
    'o_4': [],
    'o_5': ["vlan database", "no vlan 50", "vlan 50 name new_name_1",
            "vlan 1000 name new_name_2 state disable", "no vlan 100"],
    'm_1': [],
    'm_2': ["vlan database", "vlan 502 name new_vlan state disable"],
    'm_3': ["vlan database", "vlan 100 name new_name_2 state enable"],
    'm_4': [],
    'm_5': ["vlan database", "vlan 1002 name new_vlan", "vlan 502 name new_name"],
    'm_6': [],
    'm_7': ["vlan database", "vlan 32"],
    'm_8': [],
    'm_9': ["vlan database", "vlan 102 name test_vlan_1 state enable"],
    'r_1': [],
    'r_2': ["vlan database", "vlan 231 name new_vlan state enable"],
    'r_3': ["vlan database", "no vlan 50", "vlan 50 name new_name state disable"],
    'r_4': ["vlan database", "no vlan 50", "vlan 50 state disable"],
    'r_5': [],
    'r_6': ["vlan database", "no vlan 50", "vlan 50 name new_name_2", "vlan 101 state enable"],
    'd_1': [],
    'd_2': ["vlan database", "no vlan 50"],
    'd_3': ["vlan database", "no vlan 50"],
    'd_4': ["vlan database", "no vlan 50", "no vlan 100"],
    'd_5': [],
    'd_6': [],
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
    op = run_playbook('test_awplus_vlans.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_vlans.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_with_new_vlan():
    assert run_a_test('o_2')


def test_override_existing_vlan():
    assert run_a_test('o_3')


def test_override_idempotency_test():
    assert run_a_test('o_4')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_vlan():
    assert run_a_test('m_2')


def test_merge_existing_vlan():
    assert run_a_test('m_3')


def test_merge_idempotency_test():
    assert run_a_test('m_4')


def test_merge_multiple_vlans():
    assert run_a_test('m_5')


def test_merge_provide_name_only():
    assert run_a_test('m_6')


def test_merge_provide_vlan_id_only():
    assert run_a_test('m_7')


def test_merge_out_of_range_vlan_id():
    assert run_a_test('m_8')


def test_merge_new_vlan_with_existing_name():
    assert run_a_test('m_9')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_with_new_vlan():
    assert run_a_test('r_2')


def test_replace_existing_vlan():
    assert run_a_test('r_3')


def test_replace_part_of_existing_vlan():
    assert run_a_test('r_4')


def test_replace_give_only_vlan_id():
    assert run_a_test('r_5')


def test_replace_multiple_vlans():
    assert run_a_test('r_6')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_vlan_with_id():
    assert run_a_test('d_2')


def test_delete_vlan_item():
    assert run_a_test('d_3')


def test_delete_multiple_vlans():
    assert run_a_test('d_4')


def test_delete_from_incorrect_config():
    assert run_a_test('d_5')


def test_delete_non_existing_vlan():
    assert run_a_test('d_6')
