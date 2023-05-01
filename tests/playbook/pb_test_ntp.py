import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'r_1': [],
    'r_2': ["ntp server 1.1.1.4"],
    'r_3': ["no ntp server 1.1.1.3"],
    'r_4': ["no ntp authentication-key 4", "ntp authentication-key 4 md5 new_message"],
    'r_5': ["no ntp authentication-key 4", "ntp authentication-key 4 sha1 test"],
    'r_6': ["no ntp authentication-key 4", "ntp authentication-key 44122 md5 test"],
    'r_7': ["ntp source 1.2.2.2"],
    'r_8': [],
    'm_1': [],
    'm_2': ["ntp server 1.1.5.5"],
    'm_3': ["ntp source 1.1.12.1"],
    'm_4': ["no ntp authentication-key 4", "ntp authentication-key 4 md5 new key"],
    'm_5': ["no ntp authentication-key 4", "ntp authentication-key 4 sha1 test"],
    'm_6': ["ntp authentication-key 1212331 md5 test"],
    'm_7': [],
    'm_8': [],
    'm_9': [],
    'm_10': [],
    'd_1': [],
    'd_2': ["no ntp server 1.1.1.3", "no ntp server 1.1.1.2"],
    'd_3': ["no ntp server 1.1.1.2"],
    'd_4': ["no ntp source"],
    'd_5': ["no ntp authentication-key 4"],
    'o_1': ["no ntp server 1.1.1.3", "no ntp server 1.1.1.2", "no ntp authentication-key 4", "no ntp source"],
    'o_2': ["no ntp server 1.1.1.3", "no ntp server 1.1.1.2",
            "ntp server 2.1.2.1", "ntp server 2.2.2.2"],
    'o_3': ["no ntp source", "ntp source 5.5.1.1"],
    'o_4': ["no ntp authentication-key 4", "ntp authentication-key 412312 sha1 tester"],
    'o_5': ["no ntp server 1.1.1.3", "no ntp server 1.1.1.2",
            "no ntp authentication-key 4", "no ntp source", "ntp server 1.1.7.2",
            "ntp authentication-key 412312 sha1 awplus", "ntp source 1.2.1.2"],
    'o_6': [],
    'o_7': ["no ntp authentication-key 4"],
    'o_8': ["no ntp source"],
    'o_9': ["no ntp server 1.1.1.3", "no ntp server 1.1.1.2"]
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
    op = run_playbook('test_awplus_ntp.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_ntp.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_add_new_server_with_replace():
    assert run_a_test('r_2')


def test_remove_server_with_replace():
    assert run_a_test('r_3')


def test_replace_change_authentication_key():
    assert run_a_test('r_4')


def test_replace_key_type():
    assert run_a_test('r_5')


def test_replace_key_id():
    assert run_a_test('r_6')


def test_replace_source_address():
    assert run_a_test('r_7')


def test_replace_idempotency_test():
    assert run_a_test('r_8')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_server():
    assert run_a_test('m_2')


def test_merge_change_source_address():
    assert run_a_test('m_3')


def test_merge_change_authentication_key():
    assert run_a_test('m_4')


def test_merge_change_authentication_type():
    assert run_a_test('m_5')


def test_merge_new_authentication_Config():
    assert run_a_test('m_6')


def test_merge_idempotent_config():
    assert run_a_test('m_7')


def test_merge_insufficient_authentication_config_1():
    assert run_a_test('m_8')


def test_merge_insufficient_authentication_config_2():
    assert run_a_test('m_9')


def test_merge_insufficient_authentication_config_3():
    assert run_a_test('m_10')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_all_servers():
    assert run_a_test('d_2')


def test_delete_one_server():
    assert run_a_test('d_3')


def test_delete_source_address():
    assert run_a_test('d_4')


def test_delete_authentication_config():
    assert run_a_test('d_5')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_server():
    assert run_a_test('o_2')


def test_override_source_address():
    assert run_a_test('o_3')


def test_override_authentication():
    assert run_a_test('o_4')


def test_override_entire_config():
    assert run_a_test('o_5')


def test_override_idempotent_config():
    assert run_a_test('o_6')


def test_override_remove_authentication():
    assert run_a_test('o_7')


def test_override_remove_source_address():
    assert run_a_test('o_8')


def test_override_remove_servers():
    assert run_a_test('o_9')
