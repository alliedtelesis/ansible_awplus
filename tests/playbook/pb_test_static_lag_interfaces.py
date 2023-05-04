import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'override1': ["interface port1.1.8", "static-channel-group 33"],
    'override2': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33"],
    'override3': ["interface port1.1.1", "no static-channel-group",
                  "interface port1.1.3", "no static-channel-group",
                  "interface port1.1.1", "static-channel-group 33 member-filters",
                  "interface port1.1.3", "static-channel-group 33 member-filters"],
    'override4': ["interface port1.1.1", "no static-channel-group",
                  "interface port1.1.3", "no static-channel-group",
                  "interface port1.1.1", "static-channel-group 33 member-filters",
                  "interface port1.1.3", "static-channel-group 33 member-filters",
                  "interface port1.1.8", "static-channel-group 33 member-filters"],
    'override5': ["interface port1.1.1", "no static-channel-group",
                  "interface port1.1.3", "no static-channel-group",
                  "interface port1.1.1", "static-channel-group 33 member-filters",
                  "interface port1.1.3", "static-channel-group 33 member-filters",
                  "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters"],
    'override6': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33",
                  "interface port1.1.1", "no static-channel-group",
                  "interface port1.1.1", "static-channel-group 55 member-filters"],
    'override7': ["interface port1.1.1", "no static-channel-group",
                  "interface port1.1.3", "no static-channel-group",
                  "interface port1.1.3", "static-channel-group 33 member-filters",
                  "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters",
                  "interface port1.1.1", "static-channel-group 55 member-filters"],
    'override8': ["interface port1.1.2", "no static-channel-group",
                  "interface port1.1.4", "no static-channel-group",
                  "interface port1.1.5", "no static-channel-group",
                  "interface port1.1.6", "no static-channel-group",
                  "interface port1.1.7", "no static-channel-group",
                  "interface port1.1.2", "static-channel-group 33",
                  "interface port1.1.1", "no static-channel-group",
                  "interface port1.1.1", "static-channel-group 55",
                  "interface port1.1.4", "static-channel-group 55",
                  "interface port1.1.5", "static-channel-group 55",
                  "interface port1.1.6", "static-channel-group 55",
                  "interface port1.1.7", "static-channel-group 55"],
    'override9': ["interface port1.1.1", "no static-channel-group",
                  "interface port1.1.3", "no static-channel-group",
                  "interface port1.1.2", "no static-channel-group",
                  "interface port1.1.4", "no static-channel-group",
                  "interface port1.1.5", "no static-channel-group",
                  "interface port1.1.6", "no static-channel-group",
                  "interface port1.1.7", "no static-channel-group",
                  "interface port1.1.2", "static-channel-group 33 member-filters",
                  "interface port1.1.3", "static-channel-group 33 member-filters",
                  "interface port1.1.1", "static-channel-group 55",
                  "interface port1.1.4", "static-channel-group 55",
                  "interface port1.1.5", "static-channel-group 55",
                  "interface port1.1.6", "static-channel-group 55",
                  "interface port1.1.7", "static-channel-group 55"],
    'override10': ["interface port1.1.1", "no static-channel-group",
                   "interface port1.1.3", "no static-channel-group",
                   "interface port1.1.2", "no static-channel-group",
                   "interface port1.1.4", "no static-channel-group",
                   "interface port1.1.5", "no static-channel-group",
                   "interface port1.1.6", "no static-channel-group",
                   "interface port1.1.7", "no static-channel-group"],
    'override11': [],
    'merge0': [],
    'merge1': ["interface port1.1.8", "static-channel-group 33"],
    'merge2': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33"],
    'merge3': ["interface port1.1.1", "no static-channel-group",
               "interface port1.1.3", "no static-channel-group",
               "interface port1.1.1", "static-channel-group 33 member-filters",
               "interface port1.1.3", "static-channel-group 33 member-filters"],
    'merge4': ["interface port1.1.1", "no static-channel-group",
               "interface port1.1.3", "no static-channel-group",
               "interface port1.1.8", "static-channel-group 33 member-filters",
               "interface port1.1.1", "static-channel-group 33 member-filters",
               "interface port1.1.3", "static-channel-group 33 member-filters"],
    'merge5': ["interface port1.1.1", "no static-channel-group",
               "interface port1.1.3", "no static-channel-group",
               "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters",
               "interface port1.1.1", "static-channel-group 33 member-filters",
               "interface port1.1.3", "static-channel-group 33 member-filters"],
    'merge6': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33",
               "interface port1.1.1", "no static-channel-group", "static-channel-group 55 member-filters"],
    'merge7': ["interface port1.1.1", "no static-channel-group",
               "interface port1.1.3", "no static-channel-group",
               "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters",
               "interface port1.1.3", "static-channel-group 33 member-filters",
               "interface port1.1.1", "static-channel-group 55 member-filters"],
    'merge8': ["interface port1.1.2", "no static-channel-group",
               "interface port1.1.4", "no static-channel-group",
               "interface port1.1.5", "no static-channel-group",
               "interface port1.1.6", "no static-channel-group",
               "interface port1.1.7", "no static-channel-group",
               "interface port1.1.2", "static-channel-group 33",
               "interface port1.1.1", "no static-channel-group", "static-channel-group 55",
               "interface port1.1.4", "static-channel-group 55",
               "interface port1.1.5", "static-channel-group 55",
               "interface port1.1.6", "static-channel-group 55",
               "interface port1.1.7", "static-channel-group 55"],
    'merge9': ["interface port1.1.1", "no static-channel-group",
               "interface port1.1.3", "no static-channel-group",
               "interface port1.1.2", "no static-channel-group",
               "interface port1.1.4", "no static-channel-group",
               "interface port1.1.5", "no static-channel-group",
               "interface port1.1.6", "no static-channel-group",
               "interface port1.1.7", "no static-channel-group",
               "interface port1.1.2", "static-channel-group 33 member-filters",
               "interface port1.1.3", "static-channel-group 33 member-filters",
               "interface port1.1.1", "static-channel-group 55",
               "interface port1.1.4", "static-channel-group 55",
               "interface port1.1.5", "static-channel-group 55",
               "interface port1.1.6", "static-channel-group 55",
               "interface port1.1.7", "static-channel-group 55"],
    'replace0': [],
    'replace1': ["interface port1.1.8", "static-channel-group 33"],
    'replace2': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33"],
    'replace3': ["interface port1.1.1", "no static-channel-group",
                 "interface port1.1.3", "no static-channel-group",
                 "interface port1.1.1", "static-channel-group 33 member-filters",
                 "interface port1.1.3", "static-channel-group 33 member-filters"],
    'replace4': ["interface port1.1.1", "no static-channel-group",
                 "interface port1.1.3", "no static-channel-group",
                 "interface port1.1.1", "static-channel-group 33 member-filters",
                 "interface port1.1.3", "static-channel-group 33 member-filters",
                 "interface port1.1.8", "static-channel-group 33 member-filters"],
    'replace5': ["interface port1.1.1", "no static-channel-group",
                 "interface port1.1.3", "no static-channel-group",
                 "interface port1.1.1", "static-channel-group 33 member-filters",
                 "interface port1.1.3", "static-channel-group 33 member-filters",
                 "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters"],
    'replace6': ["interface port1.1.2", "no static-channel-group", "static-channel-group 33",
                 "interface port1.1.1", "no static-channel-group",
                 "interface port1.1.1", "static-channel-group 55 member-filters"],
    'replace7': ["interface port1.1.1", "no static-channel-group",
                 "interface port1.1.3", "no static-channel-group",
                 "interface port1.1.3", "static-channel-group 33 member-filters",
                 "interface port1.1.2", "no static-channel-group", "static-channel-group 33 member-filters",
                 "interface port1.1.1", "static-channel-group 55 member-filters"],
    'replace8': ["interface port1.1.2", "no static-channel-group",
                 "interface port1.1.4", "no static-channel-group",
                 "interface port1.1.5", "no static-channel-group",
                 "interface port1.1.6", "no static-channel-group",
                 "interface port1.1.7", "no static-channel-group",
                 "interface port1.1.2", "static-channel-group 33",
                 "interface port1.1.1", "no static-channel-group",
                 "interface port1.1.1", "static-channel-group 55",
                 "interface port1.1.4", "static-channel-group 55",
                 "interface port1.1.5", "static-channel-group 55",
                 "interface port1.1.6", "static-channel-group 55",
                 "interface port1.1.7", "static-channel-group 55"],
    'replace9': ["interface port1.1.1", "no static-channel-group",
                 "interface port1.1.3", "no static-channel-group",
                 "interface port1.1.2", "no static-channel-group",
                 "interface port1.1.4", "no static-channel-group",
                 "interface port1.1.5", "no static-channel-group",
                 "interface port1.1.6", "no static-channel-group",
                 "interface port1.1.7", "no static-channel-group",
                 "interface port1.1.2", "static-channel-group 33 member-filters",
                 "interface port1.1.3", "static-channel-group 33 member-filters",
                 "interface port1.1.1", "static-channel-group 55",
                 "interface port1.1.4", "static-channel-group 55",
                 "interface port1.1.5", "static-channel-group 55",
                 "interface port1.1.6", "static-channel-group 55",
                 "interface port1.1.7", "static-channel-group 55"],
    'delete0': [],
    'delete1': ["interface port1.1.1", "no static-channel-group"],
    'delete2': ["interface port1.1.1", "no static-channel-group",
                "interface port1.1.3", "no static-channel-group"],
    'delete3': ["interface port1.1.1", "no static-channel-group"],
    'delete4': ["interface port1.1.1", "no static-channel-group",
                "interface port1.1.3", "no static-channel-group"],
    'delete5': ["interface port1.1.3", "no static-channel-group",
                "interface port1.1.4", "no static-channel-group"],
    'delete6': ["interface port1.1.1", "no static-channel-group",
                "interface port1.1.3", "no static-channel-group"],
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
    op = run_playbook('test_awplus_static_lag_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_static_lag_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_override_add_new_port():
    assert run_a_test('override1')


def test_override_add_port_from_group_55():
    assert run_a_test('override2')


def test_override_member_filters_change():
    assert run_a_test('override3')


def test_override_member_filters_change_add_new_port():
    assert run_a_test('override4')


def test_override_member_filters_change_add_port_from_group_55():
    assert run_a_test('override5')


def test_override_swap_ports():
    assert run_a_test('override6')


def test_override_swap_ports_change_group_33_filters():
    assert run_a_test('override7')


def test_override_swap_ports_change_group_55_filters():
    assert run_a_test('override8')


def test_override_swap_ports_change_filters_both_groups():
    assert run_a_test('override9')


def test_override_wipe_out_everything():
    assert run_a_test('override10')


def test_override_same_port_two_groups():
    assert run_a_test('override11')


def test_merge_do_nothing():
    assert run_a_test('merge0')


def test_merge_add_port():
    assert run_a_test('merge1')


def test_merge_add_port_from_group_55():
    assert run_a_test('merge2')


def test_merge_member_filters_change():
    assert run_a_test('merge3')


def test_merge_member_filters_change_add_new_port():
    assert run_a_test('merge4')


def test_merge_member_filters_change_add_port_from_group_55():
    assert run_a_test('merge5')


def test_merge_swap_ports():
    assert run_a_test('merge6')


def test_merge_swap_ports_change_filters_group_33():
    assert run_a_test('merge7')


def test_merge_swap_ports_change_filters_group_55():
    assert run_a_test('merge8')


def test_merge_change_filters_both_groups():
    assert run_a_test('merge9')


def test_replaced_do_nothing():
    assert run_a_test('replace0')


def test_replaced_add_new_port():
    assert run_a_test('replace1')


def test_replaced_add_port_from_group_55():
    assert run_a_test('replace2')


def test_replaced_member_filters_change():
    assert run_a_test('replace3')


def test_replaced_member_filters_change_add_new_port():
    assert run_a_test('replace4')


def test_replaced_member_filters_change_add_port_from_group_55():
    assert run_a_test('replace5')


def test_replaced_swap_ports():
    assert run_a_test('replace6')


def test_replaced_swap_ports_change_group_33_filters():
    assert run_a_test('replace7')


def test_replaced_swap_ports_change_group_55_filters():
    assert run_a_test('replace8')


def test_replaced_swap_ports_change_filters_in_both_groups():
    assert run_a_test('replace9')


def test_deleted_do_nothing():
    assert run_a_test('delete0')


def test_delete_one_port():
    assert run_a_test('delete1')


def test_delete_all_ports():
    assert run_a_test('delete2')


def test_delete_one_port_change_member_filters():
    assert run_a_test('delete3')


def test_delete_all_ports_change_member_filters():
    assert run_a_test('delete4')


def test_delete_from_two_groups():
    assert run_a_test('delete5')


def test_delete_whole_group():
    assert run_a_test('delete6')
