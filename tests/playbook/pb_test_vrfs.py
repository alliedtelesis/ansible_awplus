import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'override_err1': [],
    'override_err2': [],
    'override1': ["no ip vrf bob", "no ip vrf bill", "ip vrf bill 2", " description Bill's network", " router-id 2.2.2.3",
                  " max-static-routes 234", " import map mapi2", " export map mape2", " max-fib-routes 345", " rd 62345:5",
                  " route-target both 62345:2"],
    'override2': ["no ip vrf bob", "no ip vrf bill"],
    'merge_err1': [],
    'merge_err2': [],
    'merge_err3': [],
    'merge_err4': [],
    'merge_err5': [],
    'merge_err6': [],
    'merge0': [],
    'merge1': ["no ip vrf bob", "ip vrf bob 1", " description Bob's network", " router-id 2.2.2.2", " max-static-routes 123",
               " import map mapi1", " export map mape1", " max-fib-routes 234 67", "ip vrf bob 1", " rd 62345:2"],
    'merge2': ["no ip vrf bill", "ip vrf bill 2", " description Bill's network", " router-id 2.2.2.3", " max-static-routes 234",
               " route-target import 62345:2", " route-target export 62345:3", " route-target both 62345:4",
               " import map mapi2", " export map mape2", " max-fib-routes 345", "ip vrf bill 2", " rd 62345:2"],
    'merge3': ["ip vrf bob 1", " description Bob's new network", " import map mapi4"],
    'merge4': ["no ip vrf bob", "ip vrf bob 1", " description Bob's network", " router-id 2.2.2.2", " max-static-routes 123",
               " import map mapi1", " export map mape1", " max-fib-routes 234 67", "ip vrf bob 1",
               " description Bob's new network", " rd 62345:6"],
    'merge5': ["ip vrf bill 2", " no route-target import 62345:2", " no route-target export 62345:3", " no route-target both 62345:4",
               "ip vrf bill 2", " route-target import 62345:2", " route-target import 62345:3", " route-target import 62345:4"],
    'merge6': ["ip vrf bill 2", " no route-target import 62345:2", " no route-target export 62345:3", " no route-target both 62345:4",
               "ip vrf bill 2", " route-target export 62345:2", " route-target export 62345:3", " route-target export 62345:4"],
    'merge7': ["ip vrf bill 2", " no route-target import 62345:2", " no route-target export 62345:3", " no route-target both 62345:4",
               "ip vrf bill 2", " route-target both 62345:2", " route-target both 62345:3", " route-target both 62345:4"],
    'merge8': ["ip vrf bill 2", " no route-target import 62345:2", "ip vrf bill 2", " route-target both 62345:2"],
    'merge9': ["ip vrf bill 2", " no route-target both 62345:4", "ip vrf bill 2", " route-target import 62345:4"],
    'merge10': ["ip vrf bill 2", " no route-target import 62345:2", "ip vrf bill 2", " route-target export 62345:2"],
    'merge11': ["no ip vrf bill", "ip vrf bill 2", " description Bill's network", " router-id 2.2.2.3", " max-static-routes 234",
                " import map mapi2", " export map mape2", " max-fib-routes 345", " route-target import 62345:2",
                " route-target export 62345:3", " route-target both 62345:4", "ip vrf bill 2", " no route-target import 62345:2",
                "ip vrf bill 2", " rd 62345:6", " route-target export 62345:2"],
    'merge12': ["ip vrf bill 2", " route-target export 62345:5"],
    'replace_err1': [],
    'replace_err2': [],
    'replace_err3': [],
    'replace_err4': [],
    'replace_err5': [],
    'replace_err6': [],
    'replace0': [],
    'replace1': ["no ip vrf bill", "ip vrf bill 2", " description Bill's network", " router-id 2.2.2.3", " max-static-routes 234",
                 " import map mapi2", " export map mape2", " max-fib-routes 345", " rd 62345:5", " route-target both 62345:2"],
    'delete0': [],
    'delete1': ["no ip vrf bob"],
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
    op = run_playbook('test_awplus_vrfs.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_vrfs.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_override_invalid_combination_1():
    assert run_a_test('override_err1')


def test_override_invalid_combination_2():
    assert run_a_test('override_err2')


def test_override_change_rd_delete_vrf_change_route_targets():
    assert run_a_test('override1')


def test_override_wipe_all_vrfs():
    assert run_a_test('override2')


def test_merge_invalid_combination_1():
    assert run_a_test('merge_err1')


def test_merge_invalid_combination_2():
    assert run_a_test('merge_err2')


def test_merge_invalid_combination_3():
    assert run_a_test('merge_err3')


def test_merge_invalid_combination4():
    assert run_a_test('merge_err4')


def test_merge_invalid_combination_5():
    assert run_a_test('merge_err5')


def test_merge_invalid_combination_6():
    assert run_a_test('merge_err6')


def test_merge_empty_config():
    assert run_a_test('merge0')


def test_merge_change_bobs_rd():
    assert run_a_test('merge1')


def test_merge_change_bills_rd():
    assert run_a_test('merge2')


def test_merge_change_parameters():
    assert run_a_test('merge3')


def test_merge_change_rd_and_description():
    assert run_a_test('merge4')


def test_merge_route_target_all_import():
    assert run_a_test('merge5')


def test_merge_route_target_all_export():
    assert run_a_test('merge6')


def test_merge_route_target_all_both():
    assert run_a_test('merge7')


def test_merge_route_target_one_both():
    assert run_a_test('merge8')


def test_merge_route_target_one_import():
    assert run_a_test('merge9')


def test_merge_route_target_one_export():
    assert run_a_test('merge10')


def test_merge_route_target_rd_change():
    assert run_a_test('merge11')


def test_merge_new_route_target():
    assert run_a_test('merge12')


def test_replace_invalid_config_1():
    assert run_a_test('replace_err1')


def test_replace_invalid_config_2():
    assert run_a_test('replace_err2')


def test_replace_invalid_config_3():
    assert run_a_test('replace_err3')


def test_replace_invalid_config_4():
    assert run_a_test('replace_err4')


def test_replace_invalid_config_5():
    assert run_a_test('replace_err5')


def test_replace_invalid_config_6():
    assert run_a_test('replace_err6')


def test_replace_empty_config():
    assert run_a_test('replace0')


def test_replace_one_instance_including_rd():
    assert run_a_test('replace1')


def test_delete_empty_config():
    assert run_a_test('delete0')


def test_delete_one_vrf():
    assert run_a_test('delete1')
