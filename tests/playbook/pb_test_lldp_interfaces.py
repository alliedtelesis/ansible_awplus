import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'r_1': [],
    'r_2': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select power-management-ext",
            "lldp med-tlv-select network-policy"],
    'r_3': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select port-and-protocol-vlans",
            "no lldp tlv-select mac-phy-config", "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select link-aggregation", "no lldp tlv-select port-and-protocol-vlans",
            "lldp tlv-select system-capabilities", "lldp tlv-select vlan-names"],
    'r_4': ["interface port1.6.4", "no lldp receive", "lldp transmit"],
    'r_5': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select network-policy",
            "lldp med-tlv-select power-management-ext", "lldp tlv-select power-management",
            "lldp tlv-select protocol-ids", "lldp tlv-select vlan-names"],
    'r_6': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
            "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select port-and-protocol-vlans", "no lldp tlv-select port-description",
            "lldp med-tlv-select inventory-management", "no lldp med-tlv-select network-policy"],
    'r_7': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
            "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select port-and-protocol-vlans", "no lldp tlv-select port-description", "no lldp transmit"],
    'r_8': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select network-policy",
            "lldp med-tlv-select power-management-ext", "no lldp receive", "no lldp transmit"],
    'r_9': ["interface port1.6.4", "lldp transmit",
            "lldp med-tlv-select inventory-management", "no lldp med-tlv-select power-management-ext"],
    'r_10': ["interface port1.6.4", "lldp transmit", "lldp tlv-select system-capabilities", "lldp tlv-select port-description"],
    'r_11': ["interface port1.6.4", "no lldp receive", "lldp transmit", "lldp med-tlv-select inventory-management",
             "lldp tlv-select vlan-names", "lldp tlv-select system-description"],
    'r_12': ["interface port1.6.2", "lldp med-tlv-select network-policy", "no lldp med-tlv-select inventory-management",
             "lldp med-tlv-select power-management-ext", "no lldp med-tlv-select location", "lldp med-tlv-select network-policy",
             "interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
             "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size", "no lldp tlv-select port-description",
             "lldp tlv-select vlan-names", "interface port1.6.4", "lldp transmit"],
    'r_13': [],
    'm_1': [],
    'm_2': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select power-management-ext"],
    'm_3': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select port-and-protocol-vlans",
            "lldp tlv-select system-capabilities", "lldp tlv-select vlan-names"],
    'm_4': ["interface port1.6.4", "no lldp receive", "lldp transmit"],
    'm_5': ["interface port1.6.2", "lldp tlv-select power-management", "lldp tlv-select protocol-ids", "lldp tlv-select vlan-names"],
    'm_6': ["interface port1.6.3", "lldp med-tlv-select inventory-management", "no lldp med-tlv-select network-policy"],
    'm_7': ["interface port1.6.3", "no lldp transmit"],
    'm_8': ["interface port1.6.2", "no lldp receive", "no lldp transmit"],
    'm_9': ["interface port1.6.4", "lldp med-tlv-select inventory-management", "no lldp med-tlv-select power-management-ext"],
    'm_10': ["interface port1.6.4", "lldp tlv-select system-capabilities", "lldp tlv-select port-description"],
    'm_11': ["interface port1.6.4", "no lldp receive", "lldp transmit", "lldp med-tlv-select inventory-management",
             "no lldp med-tlv-select capabilities", "no lldp med-tlv-select power-management-ext", "lldp tlv-select vlan-names",
             "lldp tlv-select system-description"],
    'm_12': ["interface port1.6.2", "no lldp med-tlv-select location", "lldp med-tlv-select network-policy", "interface port1.6.3",
             "lldp tlv-select vlan-names", "interface port1.6.4", "lldp transmit"],
    'm_13': [],
    'd_1': [],
    'd_2': [],
    'd_3': ["interface port1.6.2", "no lldp med-tlv-select inventory-management",
            "lldp med-tlv-select network-policy", "lldp med-tlv-select power-management-ext"],
    'd_4': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
            "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size", "no lldp tlv-select port-and-protocol-vlans",
            "no lldp tlv-select port-description"],
    'd_5': ["interface port1.6.4", "lldp transmit"],
    'd_6': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select power-management-ext"],
    'd_7': ["interface port1.6.3", "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config"],
    'o_1': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select network-policy",
            "lldp med-tlv-select power-management-ext", "interface port1.6.3", "no lldp tlv-select link-aggregation",
            "no lldp tlv-select mac-phy-config", "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select port-and-protocol-vlans", "no lldp tlv-select port-description", "interface port1.6.4",
            "lldp transmit"],
    'o_2': ["interface port1.6.2", "lldp med-tlv-select power-management-ext", "interface port1.6.3",
            "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
            "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select port-and-protocol-vlans", "no lldp tlv-select port-description",
            "no lldp tlv-select link-aggregation", "no lldp tlv-select mac-phy-config",
            "lldp tlv-select system-capabilities", "interface port1.6.4", "lldp transmit"],
    'o_3': ["interface port1.6.2", "no lldp med-tlv-select inventory-management", "lldp med-tlv-select network-policy",
            "lldp med-tlv-select power-management-ext", "interface port1.6.3", "no lldp tlv-select link-aggregation",
            "no lldp tlv-select mac-phy-config", "no lldp tlv-select management-address", "no lldp tlv-select max-frame-size",
            "no lldp tlv-select port-and-protocol-vlans", "no lldp tlv-select port-description", "interface port1.6.4",
            "lldp transmit", "interface port1.6.7", "lldp med-tlv-select inventory-management",
            "no lldp med-tlv-select network-policy", "interface port1.6.8", "lldp tlv-select system-capabilities",
            "interface port1.6.9", "no lldp receive"],
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
    op = run_playbook('test_awplus_lldp_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_lldp_interfaces.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_replace_empty_config_1():
    assert run_a_test('r_1')


def test_replace_med_tlv_with_med_tlv_config():
    assert run_a_test('r_2')


def test_replace_tlv_with_tlv_config():
    assert run_a_test('r_3')


def test_replace_port_using_lldp_ads_config():
    assert run_a_test('r_4')


def test_replace_switch_med_tlv_to_tlv():
    assert run_a_test('r_5')


def test_replace_switch_tlv_to_med_tlv():
    assert run_a_test('r_6')


def test_replace_switch_tlv_to_lldp_ads():
    assert run_a_test('r_7')


def test_replace_switch_med_tlv_to_lldp_ads():
    assert run_a_test('r_8')


def test_replace_switch_lldp_ads_to_med_tlv():
    assert run_a_test('r_9')


def test_replace_lldp_ads_to_tlv():
    assert run_a_test('r_10')


def test_replace_with_config_using_all_options():
    assert run_a_test('r_11')


def test_replace_multiple_interfaces():
    assert run_a_test('r_12')


def test_replace_idempotency_test():
    assert run_a_test('r_13')


def test_merge_empty_config():
    assert run_a_test('m_1')


def test_merge_med_tlv_config_with_med_tlv_config():
    assert run_a_test('m_2')


def test_merge_tlv_config_with_tlv_config():
    assert run_a_test('m_3')


def test_merge_using_lldp_ads_config_with_lldp_config():
    assert run_a_test('m_4')


def test_merge_med_tlv_config_with_tlv_config():
    assert run_a_test('m_5')


def test_merge_tlv_config_with_med_tlv_config():
    assert run_a_test('m_6')


def test_merge_tlv_config_with_lldp_ads_config():
    assert run_a_test('m_7')


def test_merge_med_tlv_config_with_lldp_ads_config():
    assert run_a_test('m_8')


def test_merge_lldp_ads_config_with_med_tlv_config():
    assert run_a_test('m_9')


def test_merge_lldp_ads_config_with_tlv_config():
    assert run_a_test('m_10')


def test_merge_using_all_options():
    assert run_a_test('m_11')


def test_merge_multiple_interfaces():
    assert run_a_test('m_12')


def test_merge_idempotency_test():
    assert run_a_test('m_13')


def test_delete_empty_config():
    assert run_a_test('d_1')


def test_delete_unused_port_using_name():
    assert run_a_test('d_2')


def test_delete_port_with_med_tlv_config_using_name():
    assert run_a_test('d_3')


def test_delete_port_with_tlv_config_using_name():
    assert run_a_test('d_4')


def test_delete_port_with_lldp_ads_config_using_name():
    assert run_a_test('d_5')


def test_delete_items_in_med_tlv_config():
    assert run_a_test('d_6')


def test_delete_items_in_tlv_config():
    assert run_a_test('d_7')


def test_override_empty_config():
    assert run_a_test('o_1')


def test_override_existing_configs():
    assert run_a_test('o_2')


def test_override_with_new_configs():
    assert run_a_test('o_3')
