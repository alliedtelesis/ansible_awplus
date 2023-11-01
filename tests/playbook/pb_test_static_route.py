import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_1': [],
    'm_2': ["ip route vrf test 168.144.2.0/24 vlan2 21 description a new static route"],
    'm_3': ["ip route 192.168.3.0/24 NULL 21"],
    'm_4': ["ipv6 route 2100:db8::1/128 2010::1 vlan2 111 description a new description"],
    'm_5': ["no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route vrf test_2 191.144.2.0/24 vlan1 112 description a new description for a route"],
    'm_6': ["no ip route vrf test 191.144.2.0/24  vlan1",
            "ip route vrf test_2 191.144.2.0/24 vlan1 112 description a new description for a route"],
    'm_7': ["no ipv6 route 2001:db8::1/128 2001::1 vlan2", "ipv6 route 2001:db8::1/128 2010::1 vlan2 11 description description"],
    'm_8': [],
    'r_1': [],
    'r_2': [],
    'r_3': ["no ip route vrf test 191.144.2.0/24  vlan1", "ip route 191.144.2.0/24 vlan1 1 description a new item"],
    'r_4': ["no ip route vrf test 191.144.2.0/24  vlan1", "ip route 191.144.2.0/24 vlan1 1 description a new item"],
    'r_5': ["no ipv6 route 2001:db8::1/128 2001::1 vlan2", "ipv6 route 2001:db8::1/128 2101::1 vlan2 11"],
    'r_6': [],
    'd_1': [],
    'd_2': [],
    'd_3': ["no ip route vrf test 191.144.2.0/24  vlan1", "ip route 191.144.2.0/24 vlan1 112",
            "no ipv6 route 2001:db8::1/128 2001::1 vlan2", "ipv6 route 2001:db8::1/128 vlan2 description description"],
    'd_4': ["no ip route vrf test 191.144.2.0/24 vlan1"],
    'd_5': ["no ipv6 route 2001:db8::1/128 2001::1 vlan2"],
    'd_6': ["no ip route 190.144.2.0/24"],
    'o_1': ["no ip route 190.144.2.0/24 vlan2", "no ip route 190.144.2.0/24 NULL",
            "no ip route vrf test 191.144.2.0/24 vlan1", "no ipv6 route 2001:db8::1/128 2001::1 vlan2"],
    'o_2': ["no ip route 190.144.2.0/24 vlan2", "no ip route 190.144.2.0/24 NULL",
            "no ip route vrf test 191.144.2.0/24 vlan1", "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ip route 172.144.2.0/32 vlan2 21 description overwritten desp"],
    'o_3': ["no ip route 190.144.2.0/24 vlan2", "no ip route 190.144.2.0/24 NULL",
            "no ip route vrf test 191.144.2.0/24 vlan1", "no ipv6 route 2001:db8::1/128 2001::1 vlan2",
            "ip route vrf test_2 191.144.2.0/32 vlan1 12 description a static route",
            "ipv6 route 2001:db8::1/128 2001::1 vlan1 description description of something"],
    'o_4': [],
    'c_1': [],
    'c_2': [],
    'c_3': [],
    'c_4': [],
    'c_5': [],
    'c_6': [],
    'c_7': [],
    'c_8': [],
    'c_9': [],
    'c_10': [],
    'c_11': [],
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
    op = run_playbook('test_awplus_static_route.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_static_route.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config_1():
    assert run_a_test('m_1')


def test_merge_new_IPv4_static_route_1():
    assert run_a_test('m_2')


def test_merge_new_IPv4_static_route_2():
    assert run_a_test('m_3')


def test_merge_new_IPv6_static_route():
    assert run_a_test('m_4')


def test_merge_IPv4_config_1():
    assert run_a_test('m_5')


def test_merge_IPv4_config_2():
    assert run_a_test('m_6')


def test_merge_IPv6_config():
    assert run_a_test('m_7')


def test_merge_idempotent_config():
    assert run_a_test('m_8')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_nothing_with_new_config():
    assert run_a_test('r_2')


def test_replace_items_in_IPv4_config_1():
    assert run_a_test('r_3')


def test_replace_items_in_IPv4_config_2():
    assert run_a_test('r_4')


def test_replace_items_in_IPv6_config():
    assert run_a_test('r_5')


def test_replace_idempotent_config():
    assert run_a_test('r_6')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_non_existing_route():
    assert run_a_test('d_2')


def test_delete_items_in_multiple_configs():
    assert run_a_test('d_3')


def test_delete_single_IPv4_route():
    assert run_a_test('d_4')


def test_delete_single_IPv6_route():
    assert run_a_test('d_5')


def test_delete_all_routes_using_same_address():
    assert run_a_test('d_6')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_add_route_remove_others():
    assert run_a_test('o_2')


def test_override_add_update_remove_config():
    assert run_a_test('o_3')


def test_override_idempotent_config():
    assert run_a_test('o_4')


def test_config_IPv6_afi_IPv4_address_1():
    assert run_a_test('c_1')


def test_config_IPv6_afi_IPv4_address_2():
    assert run_a_test('c_2')


def test_config_invalid_IPv4_address_1():
    assert run_a_test('c_3')


def test_config_invalid_IPv4_address_2():
    assert run_a_test('c_4')


def test_config_invalid_IPv4_address_3():
    assert run_a_test('c_5')


def test_config_IPv4_afi_IPv6_address_1():
    assert run_a_test('c_6')


def test_config_use_source_address_in_IPv4_config():
    assert run_a_test('c_7')


def test_config_use_vrf_in_IPv6_config():
    assert run_a_test('c_8')


def test_config_out_of_range_admin_distance():
    assert run_a_test('c_9')


def test_config_use_non_existing_vrf():
    assert run_a_test('c_10')


def test_config_use_incorrect_netmask():
    assert run_a_test('c_11')
