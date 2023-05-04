import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'r_1': ["no banner motd"],
    'r_2': ["banner exec test456"],
    'r_3': ["banner exec something new", "banner motd something else"],
    'r_4': [],
    'r_5': ["banner exec test123", "no banner motd"],
    'm_1': [],
    'm_2': ["banner exec awplus"],
    'm_3': ["banner motd awplus"],
    'm_4': [],
    'm_5': [],
    'm_6': [],
    'd_1': [],
    'd_2': ["no banner motd"],
    'd_3': [],
    'd_4': ["no banner motd"],
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
    op = run_playbook('test_awplus_banner.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_banner.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_add_new_banner_with_replaced():
    assert run_a_test('r_2')


def test_replace_existing_config():
    assert run_a_test('r_3')


def test_replace_idempotent_config():
    assert run_a_test('r_4')


def test_replace_banner_type():
    assert run_a_test('r_5')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_config():
    assert run_a_test('m_2')


def test_merge_existing_config():
    assert run_a_test('m_3')


def test_merge_insufficient_config_1():
    assert run_a_test('m_4')


def test_merge_insufficient_config_2():
    assert run_a_test('m_5')


def test_merge_idempotent_config():
    assert run_a_test('m_6')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_config_using_banner_type():
    assert run_a_test('d_2')


def test_delete_using_text():
    assert run_a_test('d_3')


def test_delete_using_same_config():
    assert run_a_test('d_4')
