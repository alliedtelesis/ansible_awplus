import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'override1': ["interface port1.1.8", "channel-group 44 mode passive"],
    'override2': ["interface port1.1.4", "no channel-group", "channel-group 44 mode active"],
    'override3': ["interface port1.1.1", "channel-group 44 mode passive", "interface port1.1.4",
                  "channel-group 66 mode passive", "interface port1.1.5", "channel-group 66 mode active",
                  "interface port1.1.6", "channel-group 66 mode active"],
    'override4': ["interface port1.1.1", "channel-group 44 mode passive", "interface port1.1.5",
                  "channel-group 66 mode active", "interface port1.1.8", "channel-group 44 mode passive"],
    'override5': ["interface port1.1.4", "no channel-group", "channel-group 44 mode passive",
                  "interface port1.1.5", "channel-group 66 mode active"],
    'override6': ["interface port1.1.3", "no channel-group", "channel-group 66 mode active",
                  "interface port1.1.4", "no channel-group", "channel-group 44 mode passive"],
    'override7': ["interface port1.1.3", "no channel-group", "channel-group 66 mode active", "interface port1.1.4",
                  "no channel-group", "channel-group 44 mode passive", "interface port1.1.5", "channel-group 66 mode active"],
    'override8': ["interface port1.1.1", "no channel-group", "interface port1.1.2", "no channel-group",
                  "interface port1.1.3", "no channel-group", "interface port1.1.4", "no channel-group",
                  "interface port1.1.5", "no channel-group", "interface port1.1.6", "no channel-group"],
    'merge': [],
    'merge1': ["interface port1.1.8", "channel-group 44 mode active"],
    'merge2': ["interface port1.1.4", "no channel-group", "channel-group 44 mode passive"],
    'merge3': ["interface port1.1.1", "channel-group 44 mode passive"],
    'merge4': ["interface port1.1.1", "channel-group 44 mode passive",
               "interface port1.1.8", "channel-group 44 mode active"],
    'merge5': ["interface port1.1.1", "channel-group 44 mode passive", "interface port1.1.4",
               "no channel-group", "channel-group 44 mode passive"],
    'merge6': ["interface port1.1.1", "no channel-group", "channel-group 66 mode active",
               "interface port1.1.4", "no channel-group", "channel-group 44 mode active"],
    'merge7': ["interface port1.1.2", "no channel-group", "channel-group 66 mode active",
               "interface port1.1.5", "no channel-group", "channel-group 44 mode active"],
    'replace0': [],
    'replace1': ["interface port1.1.8", "channel-group 44 mode passive"],
    'replace2': ["interface port1.1.4", "no channel-group", "channel-group 44 mode active"],
    'replace3': ["interface port1.1.1", "channel-group 44 mode passive",
                 "interface port1.1.3", "channel-group 44 mode active",
                 "interface port1.1.4", "channel-group 66 mode passive",
                 "interface port1.1.5", "channel-group 66 mode active"],
    'replace4': ["interface port1.1.6", "channel-group 66 mode active",
                 "interface port1.1.8", "channel-group 66 mode passive"],
    'replace5': ["interface port1.1.3", "channel-group 44 mode active",
                 "interface port1.1.4", "no channel-group", "channel-group 44 mode active"],
    'replace6': ["interface port1.1.3", "no channel-group", "channel-group 66 mode passive",
                 "interface port1.1.4", "no channel-group", "channel-group 44 mode active"],
    'replace7': ["interface port1.1.1", "no channel-group", "channel-group 66 mode passive",
                 "interface port1.1.5", "no channel-group", "channel-group 44 mode active"],
    'replace8': ["interface port1.1.1", "no channel-group",
                 "interface port1.1.2", "no channel-group",
                 "interface port1.1.3", "no channel-group"],
    'delete0': [],
    'delete1': ["interface port1.1.1", "no channel-group"],
    'delete2': ["interface port1.1.1", "no channel-group",
                "interface port1.1.2", "no channel-group",
                "interface port1.1.3", "no channel-group",
                "interface port1.1.4", "no channel-group",
                "interface port1.1.5", "no channel-group",
                "interface port1.1.6", "no channel-group"],
    'delete3': ["interface port1.1.1", "no channel-group",
                "interface port1.1.4", "no channel-group"],
    'delete4': ["interface port1.1.1", "no channel-group",
                "interface port1.1.2", "no channel-group",
                "interface port1.1.3", "no channel-group"],
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
    op = run_playbook('test_awplus_lag_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_lag_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_override_with_new_port():
    assert run_a_test('override1')


def test_override_add_port_from_group_55():
    assert run_a_test('override2')


def test_override_change_port_modes():
    assert run_a_test('override3')


def test_override_change_port_modes_add_port():
    assert run_a_test('override4')


def test_override_move_port_change_modes():
    assert run_a_test('override5')


def test_override_swap_ports():
    assert run_a_test('override6')


def test_override_swap_ports_change_modes():
    assert run_a_test('override7')


def test_override_wipe_out_everything():
    assert run_a_test('override8')


def test_merge_do_nothing():
    assert run_a_test('merge0')


def test_merge_add_new_port():
    assert run_a_test('merge1')


def test_merge_add_port_from_group_55():
    assert run_a_test('merge2')


def test_merge_mode_change():
    assert run_a_test('merge3')


def test_merge_mode_change_add_new_port():
    assert run_a_test('merge4')


def test_merge_mode_change_move_port():
    assert run_a_test('merge5')


def test_merge_swap_ports():
    assert run_a_test('merge6')


def test_replace_do_nothing():
    assert run_a_test('replace0')


def test_replace_add_new_port():
    assert run_a_test('replace1')


def test_replace_add_port_from_group_55():
    assert run_a_test('replace2')


def test_replace_mode_changes():
    assert run_a_test('replace3')


def test_replace_mode_change_add_new_port():
    assert run_a_test('replace4')


def test_replace_mode_change_move_port():
    assert run_a_test('replace5')


def test_replace_swap_ports():
    assert run_a_test('replace6')


def test_replace_swap_ports_change_modes():
    assert run_a_test('replace7')


def test_replace_whole_group_with_nothing():
    assert run_a_test('replace8')


def test_delete_nothing():
    assert run_a_test('delete0')


def test_delete_one_port():
    assert run_a_test('delete1')


def test_delete_all_ports():
    assert run_a_test('delete2')


def test_delete_from_two_groups():
    assert run_a_test('delete3')


def test_delete_whole_group():
    assert run_a_test('delete4')
