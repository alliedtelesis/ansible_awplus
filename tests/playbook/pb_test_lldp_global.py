import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_1': [],
    'm_2': ["lldp faststart-count 1", "lldp holdtime-multiplier 9", "no lldp non-strict-med-tlv-order-check",
            "lldp notification-interval 3000", "lldp port-number-type ifindex", "lldp reinit 3",
            "lldp run", "lldp timer 170", "lldp tx-delay 40"],
    'm_3': [],
    'm_4': [],
    'm_5': [],
    'm_6': [],
    'm_7': [],
    'm_8': [],
    'r_1': ["no lldp faststart-count", "no lldp holdtime-multiplier", "no lldp non-strict-med-tlv-order-check",
            "no lldp notification-interval", "no lldp tx-delay", "no lldp timer"],
    'r_2': ["no lldp holdtime-multiplier", "no lldp notification-interval", "no lldp tx-delay",
            "no lldp timer", "lldp faststart-count 2", "lldp reinit 1",
            "no lldp non-strict-med-tlv-order-check", "lldp port-number-type ifindex"],
    'r_3': ["lldp faststart-count 2", "lldp reinit 10", "no lldp non-strict-med-tlv-order-check",
            "lldp port-number-type ifindex", "lldp notification-interval 10", "lldp run",
            "lldp timer 340", "lldp tx-delay 4"],
    'r_4': [],
    'd_1': [],
    'd_2': ['no lldp faststart-count', 'no lldp holdtime-multiplier', 'no lldp non-strict-med-tlv-order-check'],
    'd_3': ['no lldp faststart-count', 'no lldp holdtime-multiplier', 'no lldp non-strict-med-tlv-order-check',
            'no lldp notification-interval', 'no lldp tx-delay', 'no lldp timer']
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
    op = run_playbook('test_awplus_lldp_global.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_lldp_global.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_and_change_everything():
    assert run_a_test('m_2')


def test_merge_invalid_value_1():
    assert run_a_test('m_3')


def test_merge_invalid_value_2():
    assert run_a_test('m_4')


def test_merge_invalid_value_3():
    assert run_a_test('m_5')


def test_merge_invalid_value_4():
    assert run_a_test('m_6')


def test_merge_invalid_value_5():
    assert run_a_test('m_7')


def test_merge_idempotent_config():
    assert run_a_test('m_8')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_part_of_config():
    assert run_a_test('r_2')


def test_replace_all_config():
    assert run_a_test('r_3')


def test_replace_timer_and_tx_delay():
    assert run_a_test('r_4')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_some_items():
    assert run_a_test('d_2')


def test_delete_all_items():
    assert run_a_test('d_3')
