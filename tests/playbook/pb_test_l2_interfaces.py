import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    "delete_1": [],
    "delete_2": ['interface port1.0.1', 'switchport mode access', 'no switchport access vlan'],
    "delete_3": ['interface port1.0.2', 'switchport mode access', 'no switchport access vlan'],
    "delete_4": [],
    "delete_5": ['interface port1.0.1', 'no switchport access vlan'],
    "delete_6": [],
    "delete_7": [],
    "delete_8": [],
    "delete_9": ['interface port1.0.2', 'switchport trunk allowed vlan remove 7'],
    "delete_10": ['interface port1.0.2', 'switchport trunk allowed vlan remove 5', 'switchport trunk allowed vlan remove 6'],
    "delete_11": [],
    "delete_12": ['interface port1.0.2', 'switchport trunk allowed vlan remove 6', 'switchport trunk allowed vlan remove 7'],
    "delete_13": [],
    "delete_14": ['interface port1.0.2', 'no switchport trunk native vlan'],
    "delete_15": [],
    "delete_16": ['interface port1.0.4', 'no switchport trunk native vlan'],
    "delete_17": ['interface port1.0.7', 'no switchport trunk native vlan'],
    "delete_18": ['interface port1.0.7', 'switchport mode access', 'no switchport access vlan'],
    "replace_1": ['interface port1.0.3', 'switchport trunk allowed vlan add 7'],
    "replace_2": ['interface port1.0.2', 'switchport trunk allowed vlan remove 7'],
    "replace_3": ['interface port1.0.2', 'switchport trunk allowed vlan add 8', 'switchport trunk allowed vlan remove 7'],
    "replace_4": ['interface port1.0.3', 'switchport trunk native vlan 22', 'switchport trunk allowed vlan add 7',
                  'switchport trunk allowed vlan add 8', 'switchport trunk allowed vlan remove 5', 'switchport trunk allowed vlan remove 6'],
    "replace_5": ['interface port1.0.2', 'switchport trunk allowed vlan add 8', 'switchport trunk allowed vlan remove 7'],
    "replace_6": [],
    "replace_7": ['interface port1.0.3', 'switchport mode access', 'switchport access vlan 99'],
    "replace_8": ['interface port1.0.1', 'switchport mode trunk', 'switchport trunk native vlan 99',
                  'switchport trunk allowed vlan add 5', 'switchport trunk allowed vlan add 6'],
    "replace_9": [],
    "replace_10": ['interface port1.0.6', 'switchport trunk native vlan 22'],
    "replace_11": ['interface port1.0.4', 'switchport trunk native vlan none'],
    "replace_12": ['interface port1.0.7', 'switchport trunk native vlan 99'],
    "replace_13": ["interface port1.0.6", "switchport trunk allowed vlan add 9", "switchport trunk allowed vlan add 10"],
    "replace_14": ["interface port1.0.2", "switchport trunk allowed vlan add 8", "switchport trunk allowed vlan add 9",
                   "switchport trunk allowed vlan add 10", "switchport trunk allowed vlan remove 6"],
    "replace_15": ["interface port1.0.2", "switchport trunk allowed vlan add 1", "switchport trunk allowed vlan add 2",
                   "switchport trunk allowed vlan add 4", "switchport trunk allowed vlan remove 5", "switchport trunk allowed vlan remove 7"],
    "override_1": ['interface port1.0.1', 'switchport access vlan 101', 'interface port1.0.2',
                   'switchport mode access', 'switchport access vlan 102', 'interface port1.0.3',
                   'switchport mode access', 'switchport access vlan 103', 'interface port1.0.4',
                   'switchport mode access', 'switchport access vlan 104', 'interface port1.0.5',
                   'switchport access vlan 105', 'interface port1.0.6', 'switchport mode access',
                   'switchport access vlan 106', 'interface port1.0.7', 'switchport mode access',
                   'switchport access vlan 107', 'interface port1.0.8', 'switchport access vlan 108',
                   'interface port1.0.9', 'switchport access vlan 109', 'interface port1.0.10',
                   'switchport access vlan 110', 'interface port1.0.11', 'switchport access vlan 111',
                   'interface port1.0.12', 'switchport access vlan 112', 'interface port1.0.13',
                   'switchport access vlan 113', 'interface port1.0.14', 'switchport access vlan 114',
                   'interface port1.0.15', 'switchport access vlan 115', 'interface port1.0.16',
                   'switchport access vlan 116', 'interface port1.0.17', 'switchport access vlan 117',
                   'interface port1.0.18', 'switchport access vlan 118', 'interface port1.0.19',
                   'switchport access vlan 119', 'interface port1.0.20', 'switchport access vlan 120',
                   'interface port1.0.21', 'switchport access vlan 121', 'interface port1.0.22',
                   'switchport access vlan 122', 'interface port1.0.23', 'switchport access vlan 123',
                   'interface port1.0.24', 'switchport access vlan 124', 'interface port1.0.25',
                   'switchport access vlan 125', 'interface port1.0.26', 'switchport access vlan 126',
                   'interface port1.0.27', 'switchport access vlan 127', 'interface port1.0.28',
                   'switchport access vlan 128', 'interface port1.0.29', 'switchport access vlan 129',
                   'interface port1.0.30', 'switchport access vlan 130', 'interface port1.0.31',
                   'switchport access vlan 131', 'interface port1.0.32', 'switchport access vlan 132',
                   'interface port1.0.33', 'switchport access vlan 133', 'interface port1.0.34',
                   'switchport access vlan 134', 'interface port1.0.35', 'switchport access vlan 135',
                   'interface port1.0.36', 'switchport access vlan 136', 'interface port1.0.37',
                   'switchport access vlan 137', 'interface port1.0.38', 'switchport access vlan 138',
                   'interface port1.0.39', 'switchport access vlan 139', 'interface port1.0.40',
                   'switchport access vlan 140', 'interface port1.0.41', 'switchport access vlan 141',
                   'interface port1.0.42', 'switchport access vlan 142', 'interface port1.0.43',
                   'switchport access vlan 143', 'interface port1.0.44', 'switchport access vlan 144',
                   'interface port1.0.45', 'switchport access vlan 145', 'interface port1.0.46',
                   'switchport access vlan 146', 'interface port1.0.47', 'switchport access vlan 147',
                   'interface port1.0.48', 'switchport access vlan 148', 'interface port1.0.49',
                   'switchport access vlan 149', 'interface port1.0.50', 'switchport access vlan 150',
                   'interface port1.0.51', 'switchport access vlan 151', 'interface port1.0.52',
                   'switchport access vlan 152'],
    "merged_1": ['interface port1.0.3', 'switchport trunk allowed vlan add 7'],
    "merged_2": ['interface port1.0.3', 'switchport trunk native vlan 99'],
    "merged_3": ['interface port1.0.1', 'switchport access vlan 22'],
    "merged_4": ['interface port1.0.2', 'switchport trunk allowed vlan add 8', 'switchport trunk native vlan 99'],
    "merged_5": [],
    "merged_6": [],
    "merged_7": ['interface port1.0.2', 'switchport mode access', 'switchport access vlan 22'],
    "merged_8": ['interface port1.0.2', 'switchport mode access', 'switchport access vlan 99'],
    "merged_9": ['interface port1.0.1', 'switchport mode trunk', 'switchport trunk allowed vlan add 5',
                 'switchport trunk allowed vlan add 6', 'switchport trunk native vlan 22'],
    "merged_10": ['interface port1.0.1', 'switchport mode trunk', 'switchport trunk allowed vlan add 5',
                  'switchport trunk allowed vlan add 6'],
    "merged_11": ['interface port1.0.1', 'switchport mode trunk', 'switchport trunk native vlan 99'],
    "merged_12": ['interface port1.0.4', 'switchport trunk native vlan none'],
    "merged_13": ['interface port1.0.7', 'switchport trunk native vlan 99'],
    "merged_14": [],
    "merged_15": ["interface port1.0.3", "switchport trunk allowed vlan add 9", "switchport trunk allowed vlan add 10"],
    "merged_16": ["interface port1.0.2", "switchport trunk allowed vlan add 8",
                  "switchport trunk allowed vlan add 9", "switchport trunk allowed vlan add 10", "switchport trunk allowed vlan add 2"],
    "merged_17": ["interface port1.0.2", "switchport trunk allowed vlan add 1",
                  "switchport trunk allowed vlan add 2", "switchport trunk allowed vlan add 4"]
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

    pop = pop.replace("false", "False")
    pop = pop.replace("true", "True")
    pop = pop.replace("null", "None")
    pop = pop.replace('{changed: [aw2] => ', '')
    pop = pop.replace('ok: [aw2] => ', '')

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
    op = run_playbook('tests_l2_interfaces.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('tests_l2_interfaces.yml', test_name)
    pop = parse_output(op)
    return check_list(pop, tests[test_name], debug=debug)


def test_delete_1():
    assert run_a_test('delete_1')


def test_delete_2():
    assert run_a_test('delete_2')


def test_delete_3():
    assert run_a_test('delete_3')


def test_delete_4():
    assert run_a_test('delete_4')


def test_delete_5():
    assert run_a_test('delete_5')


def test_delete_6():
    assert run_a_test('delete_6')


def test_delete_7():
    assert run_a_test('delete_7')


def test_delete_8():
    assert run_a_test('delete_8')


def test_delete_9():
    assert run_a_test('delete_9')


def test_delete_10():
    assert run_a_test('delete_10')


def test_delete_11():
    assert run_a_test('delete_11')


def test_delete_12():
    assert run_a_test('delete_12')


def test_delete_13():
    assert run_a_test('delete_13')


def test_delete_14():
    assert run_a_test('delete_14')


def test_delete_15():
    assert run_a_test('delete_15')


def test_delete_16():
    assert run_a_test('delete_16')


def test_delete_17():
    assert run_a_test('delete_17')


def test_delete_18():
    assert run_a_test('delete_18')


def test_replace_1():
    assert run_a_test('replace_1')


def test_replace_2():
    assert run_a_test('replace_2')


def test_replace_3():
    assert run_a_test('replace_3')


def test_replace_4():
    assert run_a_test('replace_4')


def test_replace_5():
    assert run_a_test('replace_5')


def test_replace_6():
    assert run_a_test('replace_6')


def test_replace_7():
    assert run_a_test('replace_7')


def test_replace_8():
    assert run_a_test('replace_8')


def test_replace_9():
    assert run_a_test('replace_9')


def test_replace_10():
    assert run_a_test('replace_10')


def test_replace_11():
    assert run_a_test('replace_11')


def test_replace_12():
    assert run_a_test('replace_12')


def test_replace_13():
    assert run_a_test('replace_13')


def test_replace_14():
    assert run_a_test('replace_14')


def test_replace_15():
    assert run_a_test('replace_15')


def test_override_1():
    assert run_a_test('override_1')


def test_merged_1():
    assert run_a_test('merged_1')


def test_merged_2():
    assert run_a_test('merged_2')


def test_merged_3():
    assert run_a_test('merged_3')


def test_merged_4():
    assert run_a_test('merged_4')


def test_merged_5():
    assert run_a_test('merged_5')


def test_merged_6():
    assert run_a_test('merged_6')


def test_merged_7():
    assert run_a_test('merged_7')


def test_merged_8():
    assert run_a_test('merged_8')


def test_merged_9():
    assert run_a_test('merged_9')


def test_merged_10():
    assert run_a_test('merged_10')


def test_merged_11():
    assert run_a_test('merged_11')


def test_merged_12():
    assert run_a_test('merged_12')


def test_merged_13():
    assert run_a_test('merged_13')


def test_merged_14():
    assert run_a_test('merged_14')


def test_merged_15():
    assert run_a_test('merged_15')


def test_merged_16():
    assert run_a_test('merged_16')


def test_merged_17():
    assert run_a_test('merged_17')
