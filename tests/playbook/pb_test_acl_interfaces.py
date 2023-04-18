import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_iv_1': [],
    'm_iv_2': [],
    'm_1': [],
    'm_2': ["interface port1.6.5", "access-group test_acl_4"],
    'm_3': ["interface port1.6.6", "access-group test_acl_4"],
    'm_4': [],
    'm_5': ["interface port1.6.6", "access-group test_acl_2", "access-group test_acl_3"],
    'r_1': [],
    'r_2': ["interface port1.6.5", "no access-group test_acl_3",
            "interface port1.6.5", "access-group test_acl_4"],
    'r_3': ["interface port1.6.6", "access-group test_acl_4"],
    'r_4': ["interface port1.1.10", "no access-group test_acl_2", "no access-group test_acl_1"],
    'o_1': ["interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2"],
    'o_2': ["interface port1.6.5", "no access-group test_acl_3",
            "interface port1.1.10", "no access-group test_acl_1", "no access-group test_acl_2"],
    'o_3': ["interface port1.1.10", "no access-group test_acl_1", "no access-group test_acl_2",
            "interface port1.6.5", "no access-group test_acl_3"],
    'o_4': ["interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_2", "no access-group test_acl_1"],
    'o_5': ["interface port1.6.5", "no access-group test_acl_3", "interface port1.1.10",
            "no access-group test_acl_1", "no access-group test_acl_2",
            "interface port1.1.10", "access-group test_acl_4"],
    'd_1': [],
    'd_2': [],
    'd_3': ["interface port1.1.10", "no access-group test_acl_1"],
    'd_4': ["interface port1.6.5", "no access-group test_acl_3",
            "interface port1.1.10", "no access-group test_acl_1"],
    'd_5': ["interface port1.1.10", "no access-group test_acl_1", "no access-group test_acl_2"]
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
    op = run_playbook('test_awplus_acl_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_acl_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_invalid_config_1():
    assert run_a_test('m_iv_1')


def test_merge_invalid_config_2():
    assert run_a_test('m_iv_2')


def test_merge_empty_config_1():
    assert run_a_test('m_1')


def test_merge_occupied_port():
    assert run_a_test('m_2')


def test_merge_unoccupied_port():
    assert run_a_test('m_3')


def test_merge_using_extended_acl():
    assert run_a_test('m_4')


def test_merge_multiple_acl_interfaces():
    assert run_a_test('m_4')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_on_occupied_port():
    assert run_a_test('r_2')


def test_replace_on_unoccupied_port():
    assert run_a_test('r_3')


def test_delete_with_replace():
    assert run_a_test('r_4')


def test_overwrite_empty_config_1():
    assert run_a_test('o_1')


def test_overwrite_empty_config_2():
    assert run_a_test('o_2')


def test_overwrite_empty_config_3():
    assert run_a_test('o_3')


def test_overwrite_with_empty_acl_list():
    assert run_a_test('o_4')


def test_overwrite_with_new_config():
    assert run_a_test('o_5')


def test_delete_empty_config_1():
    assert run_a_test('d_1')


def test_delete_empty_config_2():
    assert run_a_test('d_2')


def test_delete_one_acl_interface():
    assert run_a_test('d_3')
