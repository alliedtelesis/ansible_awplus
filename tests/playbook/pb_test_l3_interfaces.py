import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "m_1": [],
    "m_2": ["interface vlan3", "ip address 10.172.192.4/24"],
    "m_3": ["interface vlan2", "ipv6 address 2000:db8::ffdf/62"],
    "m_4": ["interface vlan2", "ip address dhcp client-id vlan5 hostname test_host"],
    "m_5": ["interface vlan1", "ip address 192.172.172.6/24"],
    "m_6": ["interface vlan2", "ip address 192.172.172.6/24 secondary"],
    "m_7": ["interface vlan3", "ip address 176.172.172.6/24", "ip address 192.176.172.6/24"],
    "m_8": ["interface vlan3", "ipv6 address 1000:db8::ffdf/62", "ipv6 address 1100:db8::ffdf/62"],
    "m_9": [],
    "m_10": ["interface vlan1", "ip address 192.172.172.6/24", "interface vlan6", "ipv6 address 1100:db8::ffdf/62"],
    "m_11": [],
    "m_12": ["interface vlan1", "no ip address dhcp", "ip address dhcp client-id vlan50 hostname new_name"],
    "r_1": [],
    "r_2": ["interface vlan3", "ip address 10.172.192.4/24"],
    "r_3": ["interface vlan1", "no ip address dhcp", "ip address 192.192.154.4/24",
            "no ipv6 address 2003:db8::ffdf/64", "ipv6 address 1124:db8::ffdf/62"],
    "r_4": ["interface vlan1", "no ip address dhcp", "ip address 192.192.154.4/24"],
    "r_5": ["interface vlan2", "ip address dhcp client-id vlan3 hostname test_dhcps"],
    "r_6": ["interface vlan1", "no ip address dhcp", "ip address 192.192.154.4/24",
            "no ipv6 address 2003:db8::ffdf/64", "ipv6 address 2042:db8::ffdf/64"],
    "r_7": ["interface vlan1", "no ip address dhcp", "no ipv6 address 2003:db8::ffdf/64",
            "ip address dhcp client-id vlan5 hostname test_host", "interface vlan2",
            "no ip address", "ipv6 address 2023:db8::ffdf/64"],
    "r_8": [],
    "r_9": ["interface vlan1", "no ip address dhcp", "no ipv6 address 2003:db8::ffdf/64",
            "ip address dhcp client-id vlan50 hostname new_name"],
    "o_1": [],
    "o_2": ["interface vlan1", "no ip address", "no ipv6 address 2003:db8::ffdf/64", "interface vlan2",
            "no ip address", "interface vlan3", "ip address 172.172.172.6/24"],
    "o_3": ["interface vlan2", "no ip address", "interface vlan1", "ip address 192.172.172.6/24",
            "no ipv6 2003:db8::ffdf/64", "ipv6 address 2012:db8::ffdf/64"],
    "o_4": ["interface vlan1", "no ip address", "no ipv6 address 2003:db8::ffdf/64",
            "interface vlan2", "ip address dhcp client-id vlan100 hostname test2"],
    "o_5": ["interface vlan2", "no ip address", "interface vlan1", "ip address 192.172.172.6/24"],
    "o_6": ["interface vlan2", "no ip address", "interface vlan1", "no ip address dhcp",
            "ip address dhcp client-id vlan50 hostname new_name"],
    "o_7": [],
    "o_8": ["interface vlan2", "no ip address", "interface vlan1", "no ip address dhcp", "ipv6 address 2402:db8::ffdf/64"],
    "d_1": [],
    "d_2": ["interface vlan1", "no ip address", "no ipv6 address 2003:db8::ffdf/64"],
    "d_3": [],
    "d_4": ["interface vlan1", "no ip address"],
    "d_5": []
}


def run_playbook(playbook, tag, debug=False):
    result = subprocess.run(['ansible-playbook', '-v', f'-t {tag}', f'{pb_dir}/{playbook}'], stdout=subprocess.PIPE)
    if debug:
        print(result.stdout.decode('utf-8'))
    return result.stdout.decode('utf-8')


def parse_output(op):
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
    with open('output.txt', 'a') as f:
        f.write(f"{pop}\n\n")
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
    if len(list1) != len(list2):
        if debug:
            print(list1, list2)
        return False
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            if debug:
                print(list1, list2)
            return False
    return True


def run_a_test(test_name, debug=False):
    if test_name not in tests:
        return True
    op = run_playbook('test_awplus_l3_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_l3_interfaces.yml', test_name)
    pop = parse_output(op)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_new_interface():
    assert run_a_test('m_2')


def test_merge_existing_interface():
    assert run_a_test('m_3')


def test_merge_switch_to_dhcp_from_static():
    assert run_a_test('m_4')


def test_merge_switch_to_static_from_dhcp():
    assert run_a_test('m_5')


def test_merge_secondary_address():
    assert run_a_test('m_6')


def test_merge_multiple_ipv4_addresses():
    assert run_a_test('m_7')


def test_merge_multiple_ipv6_addresses():
    assert run_a_test('m_8')


def test_merge_non_existing_interface():
    assert run_a_test('m_9')


def test_merge_multiple_interfaces():
    assert run_a_test('m_10')


def test_merge_idempotency_test():
    assert run_a_test('m_11')


def test_merge_dhcp_to_dhcp():
    assert run_a_test('m_12')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_nothing_with_new_config():
    assert run_a_test('r_2')


def test_replace_existing_config():
    assert run_a_test('r_3')


def test_replace_dhcp_to_static():
    assert run_a_test('r_4')


def test_replace_static_to_dhcp():
    assert run_a_test('r_5')


def test_replace_replace_ipv4_ipv6_addresses():
    assert run_a_test('r_6')


def test_replace_multiple_interfaces():
    assert run_a_test('r_7')


def test_replace_idempotency_test():
    assert run_a_test('r_8')


def test_replace_dhcp_dhcp():
    assert run_a_test('r_9')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_to_new_interface():
    assert run_a_test('o_2')


def test_override_existing_interface():
    assert run_a_test('o_3')


def test_override_static_to_dhcp():
    assert run_a_test('o_4')


def test_override_dhcp_to_static():
    assert run_a_test('o_5')


def test_override_dhcp_to_dhcp():
    assert run_a_test('o_6')


def test_override_idempotency_test():
    assert run_a_test('o_7')


def test_override_interface_to_ipv6():
    assert run_a_test('o_8')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_interface_using_name():
    assert run_a_test('d_2')


def test_delete_non_existing_interface():
    assert run_a_test('d_3')


def test_delete_items_in_config():
    assert run_a_test('d_4')


def test_delete_incorrectly_specified_items():
    assert run_a_test('d_5')
