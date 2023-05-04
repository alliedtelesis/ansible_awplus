import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_ic_1': [],
    'm_ic_2': [],
    'm_iv_1': [],
    'm_iv_2': [],
    'm_iv_3': [],
    'm_iv_4': [],
    'm_iv_5': [],
    'm_iv_6': [],
    'm_iv_7': [],
    'm_iv_8': [],
    'm_1': [],
    'm_2': ["access-list 104", "4 permit ip 196.146.88.0 0.0.0.255 any"],
    'm_3': ["access-list extended test2", "permit tcp 196.144.88.0/24 ne 3 any eq 54"],
    'm_4': ["access-list 104", "4 deny ip 171.42.45.0 0.0.0.255 any",
            "8 permit ip 141.143.42.0 0.0.0.255 any", "12 permit ip 181.185.85.0 0.0.0.255 any"],
    'm_5': ["access-list 104", "4 deny ip any any", "access-list 166",
            "permit ip 199.199.99.0 0.0.0.255 179.179.79.0 0.0.0.255"],
    'm_6': ["access-list 67", "deny 171.42.45.0 0.0.0.255", "access-list 153",
            "permit ip 199.199.99.0 0.0.0.255 179.179.79.0 0.0.0.255", "access-list 2006",
            "permit ip 199.199.99.0 0.0.0.255 152.152.53.0 0.0.0.255",
            "ipv6 access-list extended ipv6_test", "4 permit icmp 2001:db8::/64 2001:db8::f/60",
            "ipv6 access-list extended ipv6_test2", "deny icmp 2001:db8::/60 2001:db8::f/66"],
    'm_7': ["access-list 3001 deny icmp any any icmp-type 8"],
    'm_8': ["access-list 3000 deny icmp 171.42.45.0/24 any icmp-type 8"],
    'm_9': ["access-list hardware new_hardware_acl", "deny icmp 175.67.67.0 0.0.0.255 any icmp-type 8"],
    'm_10': ["access-list hardware hardware_acl", "4 deny ip 192.42.45.0 0.0.0.255 any",
             "8 deny udp 172.42.45.0 0.0.0.255 range 3 4 any ne 4"],
    'm_11': ["access-list extended test", "4 deny icmp 192.143.87.0/24 198.143.87.0/24 icmp-type 8"],
    'm_12': ["access-list 77"],
    'm_13': ["ipv6 access-list ipv6_hardware", "permit ip 2001:db8::f/64 2001:db8::f/64"],
    'm_ep_1': ["access-list hardware hardware_acl", "4 permit ip 192.192.92.0/24 any"],
    'm_ep_2': ["access-list extended test", "4 deny ip 192.143.87.0/24 198.143.87.0/24"],
    'm_tcp_udp_1': ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 range 2 10 any range 30 35"],
    'm_tcp_udp_2': ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 eq 10 any lt 3"],
    'm_vic_1': ["access-list extended test", "4 deny tcp 192.143.87.0/24 192.142.50.0/24"],
    'm_vic_2': ["access-list extended test", "4 deny tcp 192.143.87.0/24 192.142.50.0/24"],
    'm_vic_3': ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"],
    'm_vic_4': ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"],
    'm_vic_5': ["access-list hardware hardware_acl", "4 permit udp 192.192.92.0/24 any"],
    'm_vic_6': ["access-list extended test3", "permit udp any any lt 9"],
    'r_1': [],
    'r_2': ["access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8", "deny tcp 170.42.45.0/24 lt 9 any gt 9"],
    'r_3': [],
    'r_4': ["access-list 2001", "no deny ip 170.42.45.0 0.0.0.255 any", "no permit ip 141.143.42.0 0.0.0.255 any",
            "no permit ip 181.185.85.0 0.0.0.255 any", "permit ip 192.182.99.0 0.0.0.255 any",
            "access-list 72", "deny 180.152.66.0 0.0.0.255"],
    'r_5': ["access-list 2001", "no deny ip 170.42.45.0 0.0.0.255 any", "no permit ip 141.143.42.0 0.0.0.255 any",
            "no permit ip 181.185.85.0 0.0.0.255 any", "permit ip 192.182.99.0 0.0.0.255 any",
            "ipv6 access-list extended ipv6_test", "no deny icmp 2001:db8::/64 2001:db8::f/64",
            "deny icmp 2090:db8::/64 2001:db8::f/64"],
    'r_6': ["access-list 3000 permit udp 192.192.92.0/24 eq 2 any lt 5"],
    'r_7': ["access-list hardware hardware_acl", "no permit ip 192.192.92.0/24 any",
            "no copy-to-cpu ip 198.192.92.0/24 any", "permit udp 172.192.92.0/24 range 2 5 any eq 3"],
    'r_8': ["access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8",
            "permit icmp 172.192.92.0/24 192.192.92.0/24 icmp-type 8"],
    'r_9': ["access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50",
            "no deny icmp 196.143.87.0/24 196.142.50.0/24 icmp-type 8"],
    'r_10': [],
    'r_11': ["ipv6 access-list ipv6_test_hardware", "permit ip 2001:db8::f/63 2001:db8::f/64"],
    'o_ec_1': ["no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
               "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
               "no ipv6 access-list ipv6_test_hardware"],
    'o_ec_2': ["no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
               "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
               "no ipv6 access-list ipv6_test_hardware"],
    'o_ec_3': ["no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
               "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
               "no ipv6 access-list ipv6_test_hardware"],
    'o_1': ["no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
            "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
            "no ipv6 access-list ipv6_test_hardware", "access-list 2001", "permit ip 192.182.99.0 0.0.0.255 any"],
    'o_2': ["no access-list 72", "no access-list 104", "no access-list 2001", "no access-list extended test",
            "no ipv6 access-list extended ipv6_test", "no access-list 3000", "no access-list hardware hardware_acl",
            "no ipv6 access-list ipv6_test_hardware", "access-list 2010", "deny ip 192.182.99.0 0.0.0.255 any"],
    'o_3': [],
    'd_1': [],
    'd_2': ["access-list extended test", "no deny tcp 192.143.87.0/24 lt 1 192.142.50.0/24 eq 50"],
    'd_3': [],
    'd_4': ["no access-list 3000"],
    'd_5': ["no access-list hardware hardware_acl"],
    'd_6': ["access-list 2001", "no permit ip 141.143.42.0 0.0.0.255 any", "no permit ip 181.185.85.0 0.0.0.255 any",
            "no access-list extended test", "no access-list 72",
            "ipv6 access-list extended ipv6_test", "no deny icmp 2001:db8::/64 2001:db8::f/64"],
    'd_7': ["no access-list 72"],
    'd_8': [],
    'd_9': ["no ipv6 access-list ipv6_test_hardware"]
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
    op = run_playbook('test_awplus_acl.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_acl.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_incomplete_config_1():
    assert run_a_test('m_ic_1')


def test_merge_incomplete_config_2():
    assert run_a_test('m_ic_2')


def test_merge_invalid_config_1():
    assert run_a_test('m_iv_1')


def test_merge_invalid_config_2():
    assert run_a_test('m_iv_2')


def test_merge_invalid_config_3():
    assert run_a_test('m_iv_3')


def test_merge_invalid_config_4():
    assert run_a_test('m_iv_4')


def test_merge_invalid_config_5():
    assert run_a_test('m_iv_5')


def test_merge_invalid_config_6():
    assert run_a_test('m_iv_6')


def test_merge_invalid_config_7():
    assert run_a_test('m_iv_7')


def test_merge_invalid_config_8():
    assert run_a_test('m_iv_8')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_existing_ace():
    assert run_a_test('m_2')


def test_merge_new_acl():
    assert run_a_test('m_3')


def test_merge_multiple_aces():
    assert run_a_test('m_4')


def test_merge_multiple_acls():
    assert run_a_test('m_5')


def test_merge_acls_differant_afis():
    assert run_a_test('m_6')


def test_merge_new_numbered_hardware_acl():
    assert run_a_test('m_7')


def test_merge_new_existing_numbered_hardware_acl():
    assert run_a_test('m_8')


def test_merge_new_named_hardware_acl():
    assert run_a_test('m_9')


def test_merge_existing_named_hardware_aces():
    assert run_a_test('m_10')


def test_merge_existing_named_extended_acl():
    assert run_a_test('m_11')


def test_merge_new_acl_empty_ace():
    assert run_a_test('m_12')


def test_merge_new_ipv6_hardware_acl():
    assert run_a_test('m_13')


def test_merge_extra_params_1():
    assert run_a_test('m_eq_1')


def test_merge_extra_params_2():
    assert run_a_test('m_eq_2')


def test_merge_tcp_udp_configs_1():
    assert run_a_test('m_tcp_udp_1')


def test_merge_tcp_udp_configs_2():
    assert run_a_test('m_tcp_udp_2')


def test_merge_incorrect_tcp_udp_configs_1():
    assert run_a_test('m_vic_1')


def test_merge_incorrect_tcp_udp_configs_2():
    assert run_a_test('m_vic_2')


def test_merge_incorrect_tcp_udp_configs_3():
    assert run_a_test('m_vic_3')


def test_merge_incorrect_tcp_udp_configs_4():
    assert run_a_test('m_vic_4')


def test_merge_incorrect_tcp_udp_configs_5():
    assert run_a_test('m_vic_5')


def test_merge_incorrect_tcp_udp_configs_6():
    assert run_a_test('m_vic_6')


def test_replace_empty_config():
    assert run_a_test('r_1')


def test_replace_single_ace_in_existing_acl():
    assert run_a_test('r_2')


def test_replace_nothing_with_new_acl():
    assert run_a_test('r_3')


def test_replace_multiple_acls():
    assert run_a_test('r_4')


def test_replace_acls_different_afis():
    assert run_a_test('r_5')


def test_replace_numbered_hardware_acl():
    assert run_a_test('r_6')


def test_replace_ace_in_named_hardware_acl():
    assert run_a_test('r_7')


def test_replace_icmp_ace():
    assert run_a_test('r_8')


def test_replace_existing_acl_with_empty_config():
    assert run_a_test('r_9')


def test_replace_new_acl_no_ace():
    assert run_a_test('r_10')


def test_replace_existing_with_ipv6_hardware_acl():
    assert run_a_test('r_11')


def test_overwrite_empty_config_1():
    assert run_a_test('o_ec_1')


def test_overwrite_empty_config_2():
    assert run_a_test('o_ec_2')


def test_overwrite_empty_config_3():
    assert run_a_test('o_ec_3')


def test_overwrite_existing_acl():
    assert run_a_test('o_1')


def test_overwrite_new_acl():
    assert run_a_test('o_2')


def test_overwrite_overwrite_acl_missing_param():
    assert run_a_test('o_3')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_an_ace():
    assert run_a_test('d_2')


def test_delete_ace_of_non_existing_acl():
    assert run_a_test('d_3')


def test_delete_numbered_hardware_acl():
    assert run_a_test('d_4')


def test_delete_named_hardware_acl_with_name():
    assert run_a_test('d_5')


def test_delete_multiple_ipv4_ipv6_aces():
    assert run_a_test('d_6')


def test_delete_empty_acl():
    assert run_a_test('d_7')


def test_delete_empty_acl_provided_ace():
    assert run_a_test('d_8')


def test_delete_existing_ipv6_hardware_acl():
    assert run_a_test('d_9')
