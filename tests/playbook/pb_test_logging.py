import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_1': [],
    'm_2': ["log monitor level errors"],
    'm_3': ["log host new_log", "log host new_log level warnings facility mail"],
    'm_4': ["log permanent level warnings facility daemon"],
    'm_5': ["log external level warnings facility mail"],
    'm_6': [],
    'm_7': [],
    'm_8': [],
    'm_9': [],
    'm_10': [],
    'm_11': [],
    'm_12': [],
    'm_13': [],
    'r_1': [],
    'r_2': ["log buffered level emergencies facility kern"],
    'r_3': ["log external level emergencies facility kern", "no log external size"],
    'r_4': ["log host new_host_log", "log host new_host_log level critical facility daemon"],
    'r_5': ["log host test_name level critical facility daemon", "no log host test_name level critical facility ftp"],
    'r_6': ["no log host test_name level critical facility ftp"],
    'r_7': ["no log console level alerts facility ftp"],
    'r_8': [],
    'd_1': [],
    'd_2': ["no log console level alerts facility ftp"],
    'd_3': [],
    'd_4': [],
    'o_1': ["no log facility", "no log console level alerts facility ftp",
            "no log host test_name", "no log external size"],
    'o_2': ["log permanent size 140", "log buffered size 100", "no log facility",
            "no log console level alerts facility ftp", "no log host test_name", "no log external size"],
    'o_3': [],
    'o_4': []
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
    op = run_playbook('test_awplus_logging.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_logging.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_monitor_config():
    assert run_a_test('m_2')


def test_merge_host_log_config():
    assert run_a_test('m_3')


def test_merge_permanent_config():
    assert run_a_test('m_4')


def test_merge_external_config():
    assert run_a_test('m_5')


def test_merge_invalid_facility_value():
    assert run_a_test('m_6')


def test_merge_invalid_size():
    assert run_a_test('m_7')


def test_merge_invalid_config_1():
    assert run_a_test('m_8')


def test_merge_invalid_config_2():
    assert run_a_test('m_9')


def test_merge_invalid_config_3():
    assert run_a_test('m_10')


def test_merge_invalid_config_4():
    assert run_a_test('m_11')


def test_merge_invalid_config_5():
    assert run_a_test('m_12')


def test_merge_idempotent_config():
    assert run_a_test('m_13')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_with_new_config():
    assert run_a_test('r_2')


def test_replace_existing_external_config():
    assert run_a_test('r_3')


def test_replace_with_new_host_config():
    assert run_a_test('r_4')


def test_replace_existing_host_config():
    assert run_a_test('r_5')


def test_replace_delete_host_config_with_replaced():
    assert run_a_test('r_6')


def test_replace_delete_config_with_replaced():
    assert run_a_test('r_7')


def test_replace_idempotent_config():
    assert run_a_test('r_8')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_config():
    assert run_a_test('d_2')


def test_delete_similar_config():
    assert run_a_test('d_3')


def test_delete_non_existing_config():
    assert run_a_test('d_4')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_with_new_config():
    assert run_a_test('o_2')


def test_override_existing_configs():
    assert run_a_test('o_3')


def test_override_idempotent_config():
    assert run_a_test('o_4')
