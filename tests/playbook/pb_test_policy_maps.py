import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "r_1": [],
    "r_2": [],
    "r_3": ["policy-map test_pol_map", "no trust", "description new description", "default-action permit", "class test",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class yellow to new-dscp 63 new-bandwidth-class red", "storm-downtime 10",
            "no remark new-cos external",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"],
    "r_4": ["policy-map test_pol_map", "no trust", "description new description", "default-action permit",
            "class test", "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class yellow to new-dscp 63 new-bandwidth-class red", "storm-downtime 10",
            "no remark new-cos external", "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "class testing", "police twin-rate 128 3264 4096 4096 action drop-red",
            "storm-downtime 10", "no remark new-cos both",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class"],
    "r_5": ["policy-map test_pol_map", "no description", "no trust",
            "default-action permit", "no class test", "no class testing"],
    "r_6": ["policy-map test_pol_map", "no description", "no trust", "default-action permit",
            "class test", "storm-downtime 10", "no remark new-cos external",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"],
    "r_7": ["policy-map test_pol_map", "no trust", "description new description",
            "default-action copy-to-cpu", "class test", "remark new-cos 4 both",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class red to new-dscp 32 new-bandwidth-class yellow",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-action linkdown",
            "storm-downtime 200", "storm-rate 200", "storm-window 500", "no storm-protection",
            "set ip next-hop 172.153.43.2", "no class testing"],
    "r_8": ["policy-map test_pol_map", "no trust", "description new description",
            "default-action copy-to-cpu", "class testing", "remark new-cos 4 both",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class",
            "remark-map bandwidth-class red to new-dscp 32 new-bandwidth-class yellow",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-action linkdown",
            "storm-downtime 200", "storm-rate 200", "storm-window 500",
            "set ip next-hop 172.153.43.2", "no class test"],
    "r_9": [],
    "r_10": [],
    "r_11": ["policy-map test", "description traffic", "trust dscp", "no class tester"],
    "r_12": ["policy-map test_pol_map", "class test", "no remark new-cos external",
             "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
             "remark-map bandwidth-class yellow to new-dscp 5 ", "no police",
             "no storm-action", "no storm-downtime", "no storm-rate", "no storm-window",
             "no set ip next-hop", "no storm-protection", "no storm-downtime", "no class testing"],
    "r_13": ["policy-map test", "class test",
             "remark-map bandwidth-class yellow to new-dscp 5 ", "no class tester"],
    "m_1": [],
    "m_2": [],
    "m_3": ["policy-map test2", "trust dscp ", "description merging the config", "default-action deny",
            "class tester", "remark new-cos 5 both", "remark-map bandwidth-class red to new-dscp 3  new-bandwidth-class green",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-protection ", "storm-action portdisable",
            "storm-downtime 200", "storm-rate 100", "storm-window 500", "set ip next-hop 192.192.92.0"],
    "m_4": ["policy-map test_pol_map", "description merging a new description", "class testing",
            "remark new-cos 5 both", "remark-map bandwidth-class red to new-dscp 3  new-bandwidth-class green",
            "police single-rate 128 4096 4096 action remark-transmit", "storm-protection ",
            "storm-action vlandisable", "storm-downtime 200", "storm-rate 100",
            "storm-window 500", "set ip next-hop 192.192.92.0"],
    "m_5": [],
    "m_6": ["policy-map test_pol_map", "default-action permit", "class testing", "storm-action vlandisable",
            "storm-downtime 200", "storm-rate 100", "storm-window 500", "storm-protection "],
    "m_7": ["policy-map test_pol_map", "default-action permit", "class testing",
            "storm-action vlandisable", "class test", "remark new-cos 3 internal",
            "class tester", "police twin-rate 1000000 10240 4096 200704 action remark-transmit"],
    "m_8": ["policy-map new_pol_map", "default-action permit"],
    "m_9": ["policy-map new_pol_map", "default-action permit", "class tester"],
    "m_10": ["policy-map new_pol_map", "default-action permit", "description a new description"],
    "m_11": ["policy-map test_pol_map", "default-action permit", "class test", "no remark new-cos  external",
             "remark-map bandwidth-class yellow  to new-bandwidth-class green", "no police",
             "no storm-action", "storm-downtime 10", "no storm-rate", "no storm-window",
             "no set ip next-hop "],
    "m_12": ["policy-map test", "class test", "remark-map bandwidth-class red to new-dscp 2 "],
    "d_1": [],
    "d_2": [],
    "d_3": ["policy-map test_pol_map", "no trust ", "no description ", "default-action permit",
            "class test", "storm-downtime 10", "no remark new-cos external",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class",
            "no set ip next-hop", "no police", "no storm-protection", "no storm-window",
            "no storm-rate", "no storm-action", "no class testing"],
    "d_4": ["policy-map test_pol_map", "class testing",
            "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
            "class test", "no set ip next-hop", "no police"],
    "d_5": [],
    "d_6": [],
    "d_7": ["policy-map test_pol_map", "default-action permit", "class testing",
            "no remark-map bandwidth-class red to new-dscp new-bandwidth-class"],
    "d_8": ["policy-map test_pol_map", "class test", "storm-downtime 10", "no remark new-cos external",
            "no set ip next-hop", "no police", "no storm-window", "no storm-rate", "no storm-action"],
    "d_9": ["policy-map test", "default-action permit", "no class test"],
    "o_1": ["no policy-map test_pol_map", "no policy-map test"],
    "o_2": ["no policy-map test", "no policy-map test_pol_map"],
    "o_3": ["no policy-map test", "no policy-map test_pol_map", "policy-map new_pol_map",
            "description something something 123", "default-action send-to-mirror", "class tester",
            "police single-rate 3392 122880 229376 action remark-transmit"],
    "o_4": ["no policy-map test", "policy-map test_pol_map", "no trust", "description a different description", "default-action send-to-mirror",
            "class tester", "police single-rate 3392 122880 229376 action remark-transmit", "storm-downtime 10",
            "class test", "remark new-cos 2 internal", "storm-rate 23525", "storm-downtime 10",
            "no remark-map bandwidth-class yellow to new-dscp new-bandwidth-class", "no set ip next-hop",
            "no police", "no storm-protection", "no storm-window", "no storm-action",
            "no class testing"],
    "o_5": ["policy-map test_pol_map", "no trust", "no description", "default-action permit",
            "no class test", "no class testing", "no policy-map test"],
    "o_6": [],
    "ot_1": ["policy-map test_pol_map", "default-action permit", "class testing",
             "police single-rate 64 16769024 4096 action drop-red"],
    "ot_2": ["policy-map test_pol_map", "no trust", "no description",
             "default-action permit", "class testing",
             "police twin-rate 64 342528 4096 2355200 action remark-transmit",
             "storm-downtime 10", "no remark new-cos both",
             "no remark-map bandwidth-class green to new-dscp new-bandwidth-class",
             "no remark-map bandwidth-class red to new-dscp new-bandwidth-class",
             "no class test"],
    "ot_3": ["policy-map test_pol_map", "default-action permit", "class test",
             "remark-map bandwidth-class yellow to new-dscp 45  new-bandwidth-class green",
             "remark-map bandwidth-class green to new-dscp 32  new-bandwidth-class red",
             "remark-map bandwidth-class yellow to new-dscp 40  new-bandwidth-class red",
             "remark-map bandwidth-class red to new-dscp 4  new-bandwidth-class red",
             "remark-map bandwidth-class red to new-dscp 43  new-bandwidth-class yellow"],
    "as_1": [],
    "as_2": [],
    "as_3": [],
    "as_4": [],
    "as_5": [],
    "as_6": [],
    "as_7": [],
    "as_8": [],
    "as_9": [],
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
    op = run_playbook('test_awplus_policy_maps.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_policy_maps.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_empty_config_2():
    assert run_a_test('r_2')


def test_replace_some_of_full_config():
    assert run_a_test('r_3')


def test_replace_multiple_classes():
    assert run_a_test('r_4')


def test_delete_with_replace_1():
    assert run_a_test('r_5')


def test_delete_with_replace_2():
    assert run_a_test('r_6')


def test_replace_everything_1():
    assert run_a_test('r_7')


def test_replace_everything_2():
    assert run_a_test('r_8')


def test_replace_idempotency_test():
    assert run_a_test('r_9')


def test_replace_nothing_with_non_existent_policy_map():
    assert run_a_test('r_10')


def test_replace_with_non_existing_class():
    assert run_a_test('r_11')


def test_replace_delete_change_config_with_none_and_0():
    assert run_a_test('r_12')


def test_replace_delete_change_empty_config_with_none_and_0():
    assert run_a_test('r_13')


def test_merge_empty_config_1():
    assert run_a_test('m_1')


def test_merge_empty_config_2():
    assert run_a_test('m_2')


def test_merge_new_policy_map():
    assert run_a_test('m_3')


def test_merge_modify_elements_in_existing_policy_map():
    assert run_a_test('m_4')


def test_merge_idempotency_test():
    assert run_a_test('m_5')


def test_merge_storm_parameters_before_storm_protection():
    assert run_a_test('m_6')


def test_merge_multiple_classes():
    assert run_a_test('m_7')


def test_merge_new_policy_map_with_non_existing_class():
    assert run_a_test('m_8')


def test_merge_new_policy_map_with_class_name_only():
    assert run_a_test('m_9')


def test_merge_new_policy_map_with_no_classifier():
    assert run_a_test('m_10')


def test_merge_delete_change_with_merged():
    assert run_a_test('m_11')


def test_merge_delete_change_with_merged_with_empty_class():
    assert run_a_test('m_12')


def test_delete_empty_config_1():
    assert run_a_test('d_1')


def test_delete_empty_config_2():
    assert run_a_test('d_2')


def test_delete_everything_in_policy_map():
    assert run_a_test('d_3')


def test_delete_items_in_multiple_classes():
    assert run_a_test('d_4')


def test_delete_from_non_existing_pol_map():
    assert run_a_test('d_5')


def test_delete_non_existing_class_in_existing_policy_map():
    assert run_a_test('d_6')


def test_delete_config_that_doesnt_fully_match_have():
    assert run_a_test('d_7')


def test_delete_items_in_config_using_none_0__1():
    assert run_a_test('d_8')


def test_delete_items_in_empty_config_using_none_0__1():
    assert run_a_test('d_9')


def test_delete_class_with_name():
    assert run_a_test('d_10')


def test_override_empty_config_1():
    assert run_a_test('o_1')


def test_override_empty_config_2():
    assert run_a_test('o_2')


def test_override_with_new_policy_map():
    assert run_a_test('o_3')


def test_override_existing_policy_map():
    assert run_a_test('o_4')


def test_override_existing_policy_map_with_a_non_existent_class():
    assert run_a_test('o_5')


def test_override_idempotency_test():
    assert run_a_test('o_6')


def test_other_policer_test_1():
    assert run_a_test('ot_1')


def test_other_policer_test_2():
    assert run_a_test('ot_2')


def test_other_merge_multiple_remark_maps():
    assert run_a_test('ot_3')


def test_all_states_invalid_values_1():
    assert run_a_test('as_1')


def test_all_states_invalid_values_2():
    assert run_a_test('as_2')


def test_all_states_invalid_values_3():
    assert run_a_test('as_3')


def test_all_states_invalid_values_4():
    assert run_a_test('as_4')


def test_all_states_invalid_values_5():
    assert run_a_test('as_5')


def test_all_states_invalid_values_6():
    assert run_a_test('as_6')


def test_all_states_invalid_values_7():
    assert run_a_test('as_7')


def test_all_states_invalid_values_8():
    assert run_a_test('as_8')


def test_all_states_invalid_values_9():
    assert run_a_test('as_9')
