import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "r_1": [],
    "r_2": [],
    "r_3": ["mls qos map premark-dscp 60 to new-dscp 63"],
    "r_4": ["mls qos map premark-dscp 60 to new-dscp 63 new-cos 3"],
    "r_5": ["mls qos map premark-dscp 60 to new-dscp 63 new-cos 3 new-bandwidth-class red"],
    "r_6": ["mls qos map premark-dscp 63 to new-dscp 60 new-cos 7 new-bandwidth-class green"],
    "r_7": ["mls qos map premark-dscp 63 to new-dscp 63 new-cos 7 new-bandwidth-class yellow"],
    "r_8": [],
    "r_9": ["mls qos map premark-dscp 60 to new-dscp 3 new-cos 5 new-bandwidth-class yellow",
            "mls qos map premark-dscp 61 to new-dscp 4 new-cos 3 new-bandwidth-class red",
            "mls qos map premark-dscp 63 to new-dscp 45 new-cos 0 new-bandwidth-class green"],
    "r_10": ["mls qos map premark-dscp 63 to new-dscp 63 new-cos 0 new-bandwidth-class green"],
    "m_1": [],
    "m_2": [],
    "m_3": ["mls qos map premark-dscp 60 to new-dscp 34 new-cos 3 new-bandwidth-class red"],
    "m_4": ["mls qos map premark-dscp 63 to new-dscp 34 new-cos 3 new-bandwidth-class yellow"],
    "m_5": ["mls qos map premark-dscp 60 to new-dscp 34 new-cos 3 new-bandwidth-class yellow",
            "mls qos map premark-dscp 61 to new-dscp 23 new-cos 6 new-bandwidth-class red"],
    "m_6": [],
    "d_1": [],
    "d_2": [],
    "d_3": ["mls qos map premark-dscp 63 to new-dscp 63 new-cos 0"],
    "d_4": ["no mls qos map premark-dscp 63"],
    "d_5": [],
    "d_6": ["mls qos map premark-dscp 34 to new-cos 0", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "no mls qos map premark-dscp 63"],
    "o_1": ["no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "no mls qos map premark-dscp 63"],
    "o_2": ["no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "no mls qos map premark-dscp 63"],
    "o_3": ["no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "mls qos map premark-dscp 62 to new-cos 4 new-bandwidth-class red",
            "no mls qos map premark-dscp 63"],
    "o_4": ["no mls qos map premark-dscp 34", "no mls qos map premark-dscp 50",
            "no mls qos map premark-dscp 61", "mls qos map premark-dscp 63 to new-dscp 63 new-cos 7"],
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
    op = run_playbook('test_awplus_premark_dscps.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_premark_dscps.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_empty_config_2():
    assert run_a_test('r_2')


def test_replace_one_parameter_in_empty_map():
    assert run_a_test('r_3')


def test_replace_2_parameters_in_empty_map():
    assert run_a_test('r_4')


def test_replace_all_parameters_in_empty_map():
    assert run_a_test('r_5')


def test_replace_2_parameters_in_map_1():
    assert run_a_test('r_6')


def test_replace_2_parameters_in_map_2():
    assert run_a_test('r_7')


def test_replace_idempotency_test():
    assert run_a_test('r_8')


def test_replace_multiple_maps():
    assert run_a_test('r_9')


def test_replace_reset_map_to_default_with_replace():
    assert run_a_test('r_10')


def test_merge_an_empty_config_1():
    assert run_a_test('m_1')


def test_merge_an_empty_config_2():
    assert run_a_test('m_2')


def test_merge_a_new_config():
    assert run_a_test('m_3')


def test_merge_change_a_changed_config():
    assert run_a_test('m_4')


def test_merge_multiple_maps():
    assert run_a_test('m_5')


def test_merge_idempotency_test():
    assert run_a_test('m_6')


def test_delete_an_empty_config_1():
    assert run_a_test('d_1')


def test_delete_an_empty_config_2():
    assert run_a_test('d_2')


def test_delete_items_in_map():
    assert run_a_test('d_3')


def test_delete_map_using_dscp_in():
    assert run_a_test('d_4')


def test_delete_map_using_dscp_in_that_is_already_cleared():
    assert run_a_test('d_5')


def test_delete_multiple_maps():
    assert run_a_test('d_6')


def test_override_empty_config_1():
    assert run_a_test('o_1')


def test_override_empty_config_2():
    assert run_a_test('o_2')


def test_override_a_default_map():
    assert run_a_test('o_3')


def test_override_a_changed_map():
    assert run_a_test('o_4')


def test_invalid_input_1():
    assert run_a_test('as_1')


def test_invalid_input_2():
    assert run_a_test('as_2')


def test_invalid_input_3():
    assert run_a_test('as_3')


def test_invalid_input_4():
    assert run_a_test('as_4')


def test_invalid_input_5():
    assert run_a_test('as_5')


def test_invalid_input_6():
    assert run_a_test('as_6')
