import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'r_1': [],
    'r_2': [],
    'r_3': ["interface port1.1.1", "service-policy input test_pol_map"],
    'r_4': ["interface port1.6.2", "no service-policy input test", "service-policy input test_2"],
    'r_5': [],
    'r_6': ["interface port1.6.2", "no service-policy input test", "service-policy input pol_map",
            "interface port1.6.3", "no service-policy input test_pol_map_2", "service-policy input pol_map_2",
            "interface port1.6.5", "service-policy input test_pol_map",
            "interface port1.6.6", "service-policy input test"],
    'r_7': ["interface port1.6.1", "no service-policy input test_pol_map"],
    'r_8': [],
    'm_1': [],
    'm_2': [],
    'm_3': ["interface port1.6.4", "service-policy input test_2"],
    'm_4': ["interface port1.6.1", "no service-policy input test_pol_map", "service-policy input test_2"],
    'm_5': [],
    'm_6': [],
    'm_7': [],
    'd_1': [],
    'd_2': [],
    'd_3': ["interface port1.6.1", "no service-policy input test_pol_map"],
    'd_4': [],
    'd_5': [],
    'd_6': [],
    'd_7': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test"],
    'o_1': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_2': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_3': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2",
            "interface port1.6.9", "service-policy input test"],
    'o_4': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_5': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_6': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_7': ["interface port1.6.1", "no service-policy input test_pol_map",
            "interface port1.6.2", "no service-policy input test",
            "interface port1.6.3", "no service-policy input test_pol_map_2"],
    'o_8': [],
    'o_9': ["interface port1.6.3", "no service-policy input test_pol_map_2",
            "interface port1.6.4", "service-policy input test_pol_map_2"]
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
    op = run_playbook('test_awplus_policy_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_policy_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_empty_config_2():
    assert run_a_test('r_2')


def test_replace_on_unused_interface():
    assert run_a_test('r_3')


def test_replace_on_used_interface():
    assert run_a_test('r_4')


def test_replace_idempotency_test():
    assert run_a_test('r_5')


def test_replace_multiple_policy_interfaces():
    assert run_a_test('r_6')


def test_remove_policy_interface_with_replace():
    assert run_a_test('r_7')


def test_replace_give_only_policy_map():
    assert run_a_test('r_8')


def test_merge_empty_config_1():
    assert run_a_test('m_1')


def test_merge_empty_config_2():
    assert run_a_test('m_2')


def test_merge_policy_map_to_unused_interface():
    assert run_a_test('m_3')


def test_merge_policy_map_to_occupied_interface():
    assert run_a_test('m_4')


def test_merge_only_give_int_name():
    assert run_a_test('m_5')


def test_merge_only_give_policy_name():
    assert run_a_test('m_6')


def test_merge_using_non_existent_policy_name():
    assert run_a_test('m_7')


def test_delete_empty_config_1():
    assert run_a_test('d_1')


def test_delete_empty_config_2():
    assert run_a_test('d_2')


def test_delete_single_policy_interface():
    assert run_a_test('d_3')


def test_delete_using_int_name_only():
    assert run_a_test('d_4')


def test_delete_using_non_existent_policy_map():
    assert run_a_test('d_5')


def test_delete_using_non_existent_interface():
    assert run_a_test('d_6')


def test_delete_multiple_policy_interfaces():
    assert run_a_test('d_7')


def test_override_empty_config_1():
    assert run_a_test('o_1')


def test_override_empty_config_2():
    assert run_a_test('o_2')


def test_override_with_new_policy_map():
    assert run_a_test('o_3')


def test_override_with_incomplete_invalid_config_1():
    assert run_a_test('o_4')


def test_override_with_incomplete_invalid_config_2():
    assert run_a_test('o_5')


def test_override_with_incomplete_invalid_config_3():
    assert run_a_test('o_6')


def test_override_with_incomplete_invalid_config_4():
    assert run_a_test('o_7')


def test_override_idempotency_test():
    assert run_a_test('o_8')


def test_override_similar_config():
    assert run_a_test('o_9')
