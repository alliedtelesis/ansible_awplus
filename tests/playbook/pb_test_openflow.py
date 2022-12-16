import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "cm_1": ["openflow controller andy tcp 192.168.2.100 6653"],
    "cm_2": [],
    "cm_3": ["no openflow controller bob","openflow controller bob tcp 192.168.2.100 6653"],
    "co_1": ['no openflow controller bob', 'no openflow controller fred', 'no openflow controller dave', 'openflow controller andy tcp 192.168.2.100 6654', 'interface port1.6.1', 'no openflow', 'interface port1.6.2', 'no openflow', 'interface port1.6.3', 'no openflow', 'interface port1.6.4', 'no openflow', 'no openflow inactivity', 'no openflow native vlan', 'no openflow datapath-id', 'no openflow failmode'],
    "co_2": ['no openflow controller bob', 'no openflow controller dave', 'no openflow controller fred', 'openflow controller bob tcp 192.168.1.100 6653', 'interface port1.6.1', 'no openflow', 'interface port1.6.2', 'no openflow', 'interface port1.6.3', 'no openflow', 'interface port1.6.4', 'no openflow', 'no openflow inactivity', 'no openflow native vlan', 'no openflow datapath-id', 'no openflow failmode'],
    "co_3": ['no openflow controller dave', 'no openflow controller fred', 'no openflow controller bob', 'openflow controller bob tcp 192.168.2.100 6654', 'interface port1.6.1', 'no openflow', 'interface port1.6.2', 'no openflow', 'interface port1.6.3', 'no openflow', 'interface port1.6.4', 'no openflow', 'no openflow inactivity', 'no openflow native vlan', 'no openflow datapath-id', 'no openflow failmode'],
    "co_4": [],
    "cr_1": ['no openflow controller fred', 'no openflow controller dave', 'no openflow controller bob', 'openflow controller andy tcp 192.168.2.100 6654'],
    "cr_2": ['no openflow controller dave', 'no openflow controller bob', 'no openflow controller fred', 'openflow controller bob tcp 192.168.1.100 6653'],
    "cr_3": ['no openflow controller fred', 'no openflow controller dave', 'no openflow controller bob', 'openflow controller bob tcp 192.168.2.100 6654'],
    "cr_4": [],
    "cd_1": ["no openflow controller bob"],
    "cd_2": [],
    "p_1": ["no openflow controller bob", "no openflow controller fred", "no openflow controller dave",
            "interface port1.6.1", "no openflow", "interface port1.6.5", "openflow", "no openflow inactivity",
            "no openflow native vlan", "no openflow datapath-id", "no openflow failmode"],
    "p_2": ["no openflow controller dave", "no openflow controller fred", "no openflow controller bob",
            "interface port1.6.1", "no openflow", "interface port1.6.2", "no openflow",
            "interface port1.6.3", "no openflow", "interface port1.6.4", "no openflow",
            "no openflow inactivity", "no openflow native vlan", "no openflow datapath-id",
            "no openflow failmode"],
    "p_3": ["no openflow controller dave", "no openflow controller fred", "no openflow controller bob",
        "interface port1.6.5", "openflow", "no openflow inactivity", "no openflow native vlan",
        "no openflow datapath-id", "no openflow failmode"],
    "p_4": ["interface port1.6.5", "openflow"],
    "p_5": [],
    "p_6": ["interface port1.6.5", "openflow"],
    "p_7": [],
    "p_8": ["interface port1.6.1", "no openflow"],
    "p_9": ["interface port1.6.1", "no openflow", "interface port1.6.2", "no openflow",
            "interface port1.6.3", "no openflow", "interface port1.6.4", "no openflow"],
    "p_10": [],
    "p_11": [],
    "ip6_1": ["no openflow controller dave",
            "openflow controller dave tcp 2001:0db8:85a3:0000:0000:8a2e:0370:7339 6655"],
    "ip6_2": ["openflow controller henry tcp 2001:0db8:85a3:0000:0000:8a2e:0370:7340 6656"],
    "ip6_3": [],
    "ip6_4": ["no openflow controller bob",
            "openflow controller bob tcp 2001:0db8:85a3:0000:0000:8a2e:0370:7386 6653"],
    "ip6_5": ["no openflow controller dave", "no openflow controller fred", "no openflow controller bob",
            "openflow controller dave tcp 2001:0db8:85a3:0000:0000:8a2e:0370:7332 6655"],
    "ip6_6": ["no openflow controller dave"],
    "o_1": ["openflow native vlan 4089"],
    "o_2": ["no openflow controller dave", "no openflow controller fred", "no openflow controller bob",
            "openflow controller bob tcp 192.168.1.100 6653", "openflow controller fred tcp 192.168.1.100 6654",
            "no openflow inactivity", "no openflow native vlan", "no openflow datapath-id",
            "no openflow failmode"],
    "o_3": ["no openflow controller fred", "no openflow controller bob", "no openflow controller dave",
            "openflow native vlan 4089"],
    "o_4": ["no openflow native vlan"],
    "o_5": ["no openflow failmode"],
    "o_6": ["no openflow controller fred", "no openflow controller bob",
            "no openflow controller dave", "openflow controller bob ssl 192.168.2.100 6651"],
    "o_7": ["no openflow controller bob", "openflow controller bob ssl 192.168.5.100 6659"],
}


def run_playbook(playbook, tag, debug=False):
    result = subprocess.run(['ansible-playbook', '-v', f'-t {tag}', f'{pb_dir}/{playbook}'], stdout=subprocess.PIPE)
    # with open("output.txt", "a") as f:
    #     f.write(f"{result}\n\n\n")
    if debug:
        print(result.stdout.decode('utf-8'))
    return result.stdout.decode('utf-8')


def parse_output(op, tag='test_init'):
    looking = True
    with open("output2.txt", "a") as f:
        f.write(f"{op}\n\n")
    pop = ""
    # with open("output.txt", "a") as f:
    #     f.write(f"{op}\n\n\n")
    for outl in op.splitlines():
        ls = outl.strip()
        if looking:
            # with open("output.txt", "a") as f:
            #     f.write(f"ls: {ls}\n\n\n")
            #  and ls.endswith('{')
            if ls.startswith(('ok:', 'changed:')):
                pop = "{"
                # with open("output.txt", "a") as f:
                #     f.write(f"here {ls[-1]}\n\n\n")
                looking = False
        else:
            if ls.startswith('changed:'):
                pop += ls
                # with open("output.txt", "a") as f:
                #     f.write(f"ls {ls}\n\n")
                if outl.rstrip() == '}':
                    break

    
    pop = pop.replace("false", "False")
    pop = pop.replace("true", "True")
    # with open("output.txt", "a") as f:
    #     f.write(f"pop after {pop}\n\n")
    pop = pop.replace('{changed: [aw2] => ', '')
    try:
        pop = ast.literal_eval(pop)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return []
    with open("output.txt", "a") as f:
        f.write(f"test: {tag} commands {pop.get('commands')}\n\n")
    return pop.get('commands')


def check_list(list1, list2, debug=False):
    if len(list1) != len(list2):
        if debug:
            print(list1, list2)
        return False
    for i in range(len(list1)):
        if list1[i] not in list2:
            return False





        # if list1[i] != list2[i]:
        #     if debug:
        #         print(list1, list2)
        #     return False
    return True


def run_a_test(test_name, debug=False):
    if test_name not in tests:
        return True
    op = run_playbook('tests_openflow.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('tests_openflow.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)

def test_merge_add_a_new_controller():
    with open("output.txt", "w") as f:
        f.write(f"")
    with open("output2.txt", "w") as f:
        f.write(f"")
    assert run_a_test('cm_1')

def test_merge_new_controller_missing_parameters():
    assert run_a_test('cm_2')

def test_merge_controller_change_parameter():
    assert run_a_test('cm_3')

def test_override_one_new_controller():
    assert run_a_test('co_1')

def test_override_one_existing_controller():
    assert run_a_test('co_2')

def test_override_one_existing_controller_changed_parameters():
    assert run_a_test('co_3')

def test_override_missing_paremeter():
    assert run_a_test('co_4')

def test_replace_one_new_controller():
    assert run_a_test('cr_1')

def test_replace_one_existing_controller():
    assert run_a_test('cr_2')

def test_replace_one_existing_controller_changed_parameters():
    assert run_a_test('cr_3')

def test_replace_missing_parameter():
    assert run_a_test('cr_4')

def test_delete_delete_existing_controller():
    assert run_a_test('cd_1')

def test_delete_delete_non_existing_controller():
    assert run_a_test('cd_2')

def test_port_overide_with_new_port_deleting_one():
    assert run_a_test('p_1')

def test_port_overide_with_no_ports():
    assert run_a_test('p_2')

def test_port_overide_with_new_port():
    assert run_a_test('p_3')

def test_port_merge_with_new_port():
    assert run_a_test('p_4')

def test_port_merge_with_same_port():
    assert run_a_test('p_5')

def test_port_merge_with_new_port_plus_one():
    assert run_a_test('p_6')

def test_port_merge_with_port():
    assert run_a_test('p_7')

def test_port_delete_a_port():
    assert run_a_test('p_8')

def test_port_delete_all_ports():
    assert run_a_test('p_9')

def test_port_delete_invalid_port():
    assert run_a_test('p_10')

def test_port_delete_no_ports():
    assert run_a_test('p_11')

def test_IPv6_change_IPv6_address_parameter():
    assert run_a_test('ip6_1')

def test_IPv6_add_new_controller():
    assert run_a_test('ip6_2')

def test_IPv6_add_new_controller_with_missing_parameter():
    assert run_a_test('ip6_3')

def test_IPv6_change_from_IPv4_to_IPv6():
    assert run_a_test('ip6_4')

def test_IPv6_replace_with_new_address():
    assert run_a_test('ip6_5')

def test_delete_existing_user_with_an_IPv6_address():
    assert run_a_test('ip6_6')

def test_other_merge_leaves_other_parameters_unchanged():
    assert run_a_test('o_1')

def test_other_restore_all_to_defaults():
    assert run_a_test('o_2')

def test_other_replace_leaves_other_parameters_unchanged():
    assert run_a_test('o_3')

def test_other_delete_restores_default():
    assert run_a_test('o_4')

def test_other_fail_mode_secure():
    assert run_a_test('o_5')

def test_other_replace_multiple_parameters():
    assert run_a_test('o_6')

def test_other_merge_multiple_parameters():
    assert run_a_test('o_7')
