import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "r_1": [],
    "r_2": [],
    "r_3": ["class-map testing", "match access-group 3001", "match cos 2",
            "match dscp 3", "match eth-format 802dot2-untagged protocol f0",
            "match inner-cos 3", "match inner-vlan 7", "match ip-precedence 3",
            "match mac-type l2bcast", "match tcp-flags ack ",
            "no match tcp-flags psh rst ", "match vlan 4050"],
    "r_4": ["class-map testing", "no match eth-format protocol", "no match inner-cos ",
            "no match cos ", "no match tcp-flags fin psh rst syn urg ", "no match vlan ",
            "no match ip-precedence ", "no match dscp ", "no match access-group 3000",
            "no match inner-vlan ", "no match mac-type "],
    "r_5": ["class-map testing", "no match eth-format protocol", "no match inner-cos ",
            "no match cos ", "no match tcp-flags fin psh rst syn urg ", "no match vlan ",
            "no match ip-precedence ", "no match dscp ", "no match access-group 3000",
            "no match inner-vlan ", "no match mac-type "],
    "r_6": [],
    "r_7": [],
    "r_8": [],
    "r_9": ["class-map testing", "match inner-cos 3", "match mac-type l2ucast",
            "match tcp-flags ack ", "no match tcp-flags fin psh rst syn urg ",
            "match vlan 500", "no match ip-precedence ", "no match dscp ",
            "no match inner-vlan ", "no match eth-format protocol", "no match cos ",
            "no match access-group 3000", "class-map test", "match access-group 3000",
            "match dscp 2", "match ip-precedence 7"],
    "r_10": [],
    "r_11": ["class-map testing", "no match dscp ", "no match cos ", "no match inner-cos ",
             "no match eth-format protocol", "no match access-group 3000", "no match vlan ",
             "no match ip-precedence ", "no match inner-vlan ",
             "no match tcp-flags fin psh rst syn urg ", "no match mac-type "],
    "r_12": [],
    "r_13": ["class-map testing", "match access-group named_hardware_acl",
             "no match inner-vlan ", "no match tcp-flags fin psh rst syn urg ",
             "no match eth-format protocol", "no match cos ", "no match ip-precedence ",
             "no match vlan ", "no match mac-type ", "no match dscp ", "no match inner-cos "],
    "m_1": [],
    "m_2": [],
    "m_3": ["class-map testing", "match access-group 3001", "match cos 7", "match dscp 2",
            "match eth-format 802dot2-untagged protocol netbeui", "match inner-cos 5",
            "match inner-vlan 700", "match ip-precedence 1", "match mac-type l2bcast",
            "match tcp-flags ack ", "no match tcp-flags fin ", "match vlan 399"],
    "m_4": ["class-map test", "match cos 3", "match dscp 3", "match inner-cos 3",
            "match ip-precedence 3", "match tcp-flags psh ", "no match tcp-flags ack "],
    "m_5": ["class-map new_class_map2"],
    "m_6": ["class-map new_class_map2", "match eth-format 802dot2-untagged protocol netbeui",
            "match cos 3", "match dscp 3", "match tcp-flags syn "],
    "m_7": ["class-map test", "match access-group 3000", "match cos 5",
            "match mac-type l2mcast", "class-map new_class_map",
            "match inner-cos 3", "match tcp-flags psh ", "match vlan 302"],
    "m_8": ["class-map new_class_map"],
    "m_9": [],
    "m_10": [],
    "m_11": ["class-map testing", "match tcp-flags ack ", "no match tcp-flags fin psh "],
    "m_12": ["class-map test", "match access-group named_hardware_acl"],
    "m_13": ["class-map testing", "match access-group named_hardware_acl"],
    "d_1": [],
    "d_2": [],
    "d_3": ["no class-map testing"],
    "d_4": [],
    "d_5": ["no class-map testing", "no class-map test"],
    "d_6": ["no class-map testing"],
    "d_7": ["class-map testing", "no match access-group 3000", "no match cos",
            "no match dscp", "no match eth-format protocol", "no match inner-cos",
            "no match inner-vlan", "no match ip-precedence", "no match mac-type",
            "no match tcp-flags urg psh rst syn fin ", "no match vlan"],
    "d_8": ["class-map testing", "no match access-group 3000",
            "no match tcp-flags syn ", "no class-map test"],
    "d_9": [],
    "d_10": [],
    "d_11": ["class-map testing", "no match eth-format protocol"],
    "o_1": ["no class-map testing", "no class-map test"],
    "o_2": ["no class-map testing", "no class-map test"],
    "o_3": ["no class-map testing", "no class-map test"],
    "o_4": ["class-map testing", "match inner-cos 4", "match inner-vlan 7",
            "match ip-precedence 1", "match mac-type l2bcast", "match vlan 3",
            "no match tcp-flags fin psh rst syn urg ", "no match dscp ",
            "no match access-group 3000", "no match cos ",
            "no match eth-format protocol", "no class-map test"],
    "o_5": ["no class-map testing", "no class-map test", "class-map new-class-map",
            "match cos 3", "match vlan 3", "match tcp-flags ack syn urg "],
    "o_6": ["no class-map testing", "class-map test", "match inner-cos 5", "match vlan 390",
            "class-map new-class-map", "match mac-type l2ucast", "match tcp-flags fin "]
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
    op = run_playbook('test_awplus_class_maps.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_class_maps.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_empty_config_2():
    assert run_a_test('r_2')


def test_replace_each_element_in_config():
    assert run_a_test('r_3')


def test_replace_eth_format_only():
    assert run_a_test('r_4')


def test_replace_eth_protocol_only():
    assert run_a_test('r_5')


def test_replace_out_of_range_1():
    assert run_a_test('r_6')


def test_replace_out_of_range_2():
    assert run_a_test('r_7')


def test_replace_out_of_range_3():
    assert run_a_test('r_8')


def test_replace_2_class_maps():
    assert run_a_test('r_9')


def test_replace_nothing_with_class_map():
    assert run_a_test('r_10')


def test_replace_config_with_empty_config():
    assert run_a_test('r_11')


def test_replace_config_with_same_config():
    assert run_a_test('r_12')


def test_replace_with_named_hardware_acl():
    assert run_a_test('r_13')


def test_merge_empty_config_1():
    assert run_a_test('m_1')


def test_merge_empty_config_2():
    assert run_a_test('m_2')


def test_merge_multiple_parameters_in_existing_config():
    assert run_a_test('m_3')


def test_merge_new_parameters_in_existing_config():
    assert run_a_test('m_4')


def test_create_an_empty_class_map():
    assert run_a_test('m_5')


def test_create_a_new_class_map():
    assert run_a_test('m_6')


def test_merge_multiple_class_maps():
    assert run_a_test('m_7')


def test_create_new_class_map_but_only_provide_eth_format():
    assert run_a_test('m_8')


def test_merge_eth_protocol_with_existing_class_map():
    assert run_a_test('m_9')


def test_merge_same_config():
    assert run_a_test('m_10')


def test_toggle_tcp_flags():
    assert run_a_test('m_11')


def test_merge_named_hardware_acl():
    assert run_a_test('m_12')


def test_change_hardware_acls():
    assert run_a_test('m_13')


def test_delete_empty_config_1():
    assert run_a_test('d_1')


def test_delete_empty_config_2():
    assert run_a_test('d_2')


def test_delete_existing_class_map_with_name():
    assert run_a_test('d_3')


def test_delete_non_existing_class_map_with_name():
    assert run_a_test('d_4')


def test_delete_multiple_existing_class_maps_with_name():
    assert run_a_test('d_5')


def test_delete_existing_and_non_existing_class_map_with_name():
    assert run_a_test('d_6')


def test_delete_all_elements_in_class_map():
    assert run_a_test('d_7')


def test_delete_elements_in_multiple_class_maps():
    assert run_a_test('d_8')


def test_delete_element_with_invalid_config_1():
    assert run_a_test('d_9')


def test_delete_element_with_invalid_config_2():
    assert run_a_test('d_10')


def test_delete_eth_format_protocol_with_eth_format():
    assert run_a_test('d_11')


def test_override_with_empty_config_1():
    assert run_a_test('o_1')


def test_override_with_empty_config_2():
    assert run_a_test('o_2')


def test_override_with_empty_config_3():
    assert run_a_test('o_3')


def test_override_with_existing_config():
    assert run_a_test('o_4')


def test_override_with_new_config():
    assert run_a_test('o_5')


def test_override_multiple_class_maps():
    assert run_a_test('o_6')
