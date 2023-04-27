import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'r_1': [],
    'r_2': ["interface port1.6.3", "lacp port-priority 10"],
    'r_3': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 102"],
    'r_4': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 105",
            "interface port1.6.2", "lacp timeout short", "lacp port-priority 201"],
    'r_5': [],
    'r_6': ["interface port1.6.1", "lacp timeout long", "no lacp port-priority"],
    'r_7': ["interface port1.6.1", "no lacp port-priority"],
    'r_8': ["interface port1.6.1", "lacp timeout long"],
    'm_1': [],
    'm_2': ["interface port1.6.3", "lacp port-priority 20"],
    'm_3': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 20"],
    'm_4': [],
    'm_5': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 20",
            "interface port1.6.4", "lacp timeout short", "lacp port-priority 80"],
    'm_6': [],
    'm_7': ["interface port1.6.1", "lacp timeout long"],
    'm_8': ["interface port1.6.5", "lacp timeout short"],
    'o_1': ["interface port1.6.1", "lacp timeout long", "no lacp port-priority",
            "interface port1.6.2", "no lacp port-priority",
            "interface port1.6.5", "no lacp port-priority"],
    'o_2': ["interface port1.6.1", "lacp timeout long", "no lacp port-priority",
            "interface port1.6.2", "no lacp port-priority",
            "interface port1.6.4", "lacp port-priority 5000",
            "interface port1.6.5", "no lacp port-priority"],
    'o_3': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 5000",
            "interface port1.6.2", "no lacp port-priority",
            "interface port1.6.5", "no lacp port-priority"],
    'o_4': [],
    'o_5': ["interface port1.6.1", "lacp timeout long", "lacp port-priority 200",
            "interface port1.6.3", "lacp timeout short", "lacp port-priority 20000",
            "interface port1.6.5", "no lacp port-priority"],
    'd_1': [],
    'd_2': ["interface port1.6.1", "lacp timeout long", "no lacp port-priority"],
    'd_3': [],
    'd_4': ["interface port1.6.1", "no lacp port-priority"],
    'd_5': ["interface port1.6.1", "lacp timeout long"],
    'd_6': []
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
    op = run_playbook('test_awplus_lacp_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_lacp_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_nothing_new_config():
    assert run_a_test('r_2')


def test_replace_existing_config():
    assert run_a_test('r_3')


def test_replace_multiple_configs():
    assert run_a_test('r_4')


def test_replace_idempotency_test():
    assert run_a_test('r_5')


def test_remove_config_with_replaced():
    assert run_a_test('r_6')


def test_remove_port_priority_with_replaced():
    assert run_a_test('r_7')


def test_replace_timeout_with_replaced():
    assert run_a_test('r_8')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_config():
    assert run_a_test('m_2')


def test_merge_existing_config():
    assert run_a_test('m_3')


def test_merge_out_range_port_priority():
    assert run_a_test('m_4')


def test_merge_multiple_configs():
    assert run_a_test('m_5')


def test_merge_idempotency_test():
    assert run_a_test('m_6')


def test_merge_short_to_long():
    assert run_a_test('m_7')


def test_merge_long_to_short():
    assert run_a_test('m_8')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_with_new_config():
    assert run_a_test('o_2')


def test_override_existing_config():
    assert run_a_test('o_3')


def test_override_idempotency_test():
    assert run_a_test('o_4')


def test_override_multiple_configs():
    assert run_a_test('o_5')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_config_using_name():
    assert run_a_test('d_2')


def test_delete_non_existing_config_using_name():
    assert run_a_test('d_3')


def test_delete_port_priority():
    assert run_a_test('d_4')


def test_delete_timeout():
    assert run_a_test('d_5')


def test_delete_incorrect_config():
    assert run_a_test('d_6')
