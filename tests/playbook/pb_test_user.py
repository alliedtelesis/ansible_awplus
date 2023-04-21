import subprocess
import os
import ast

pb_dir = os.path.dirname(__file__)

tests = {
    'm_test_1': [],
    'm_test_2': [],
    'm_test_3': ["username John privilege 15 password 8 $5$beWs4hWrHY4RGTl4$ju8Nt.r6yl72AfqkKIc1VW72R4ra9X3nM2UzyrHLer5"],
    'm_test_4': ["username John privilege 15 password 8 $5$niumlS6h$ae.kFUj6zuvoedt63PFQM1T4dD.EvjHVKR3sG9VH18B"],
    'm_test_5': [],
    'm_test_6': ["username John privilege 1 password 8 $5$kcJ1qirn0dvhKLn0$Rxczwr8iuySduL7VFA8oTbadI/X5Jb3CR7YRhPlE0P0"],
    'm_test_7': [],
    'm_test_8': [],
    'm_test_9': ["username test_user password 8 $5$ZfeSXZNKkFtGaOsh$AvLzVpiZGWK7lZxtxNV447Oi9GK4czItLqBgJV3tcTA"],
    'm_test_10': ["username test_user privilege 11"],
    'm_test_11': ["username test_user privilege 5 password 8 $5$niumlS6h$ae.kFUj6zuvoedt63PFQM1T4dD.EvjHVKR3sG9VH18B"],
    'm_test_12': [],
    'm_test_13': ["username bob privilege 1 password 8 $5$xH1k.yIKmf.HyO0y$rAekVASnw8OzjQ8ja.v0lAulU79hF6t0Gaqx1aPQ914"],
    'm_test_14': ["username bill password 8 $1$uWpOyAfS$3PAKGZRtk44xYWFsIhJ8G9"],
    'm_test_15': [],
    'm_test_16': ["username bill password 8 $5$uRXfAAn95H5fo4bG$tedRlexoPG7rjOJRkAOwbyoKd6GXN8RagClqLnayjh."],
    'm_test_17': ["username Bill privilege 1 password 8 $5$uRXfAAn95H5fo4bG$tedRlexoPG7rjOJRkAOwbyoKd6GXN8RagClqLnayjh.",
                  "username Bob privilege 1 password 8 $5$4zkZU10hy4kwk2Ao$b27giLpBKXip7kqGvOlxVCOkPiNDCmVXGPmAiPU8pfC",
                  "username David privilege 1 password 8 $5$qReaGY6chtTPnkjx$lKmF6hF2zw7L1THYPnm2NWFDBJCYe1Z345MYXiVzKw0",
                  "username Anne privilege 1 password 8 $5$4VUSIR41T4xN0uu7$vjDcy7Kgv9.t7RvDZrTu77PZR4yGl/q4Xyle0A1wCT/",
                  "username Mary privilege 1 password 8 $5$WmZt2w0HDUVjcM2X$6DaV5tJCbQd8F0R776cV054DET7FD5/hU81dSqV6.ZC",
                  "username April privilege 1 password 8 $5$mahTa3ZqoN5U9YHp$HT.ea/PyUUDsalDAON59iUSS2D2SWh5pr1gjWgV4ZY1",
                  "username Thomas privilege 1 password 8 $5$AXkoQLp93itzrANk$z80kxStcPQfQdtaNaU77Ir38egpO4jEsxtJwUpmMXnC",
                  "username Percy privilege 1 password 8 $5$vBUDapAnW7/PURSR$6Jpxdf.UlEIgEDwV9owDyFVg0h1XaOPsbeZVI/uUX/7",
                  "username James privilege 1 password 8 $5$iJoYqlj0VtMJOWVW$/Fe83KeQoqfyjCwJzrjkv6JLjRt0bkEtnuVM0NVa5f9",
                  "username Gordan privilege 1 password 8 $5$EnsT9gFKhX8jvAST$PX6oiJwkFXXccU/H5/TUbfwjQDs5Irhf5aYR1TL3n51"],
    'm_test_18': [],
    'r_test_1': ["username test_user password 8 $5$nABt9VDrIVdrHht/$/3a1c3ZK9TQ4c1oi47mDnWRSsS5t6MbCH3PwV39qdq7"],
    'r_test_2': [],
    'r_test_3': ["username test_user password 8 $1$uWpOyAfS$3PAKGZRtk44xYWFsIhJ8G1"],
    'd_test_1': [],
    'd_test_2': [],
    'd_test_3': ["no username test_user"],
    'd_test_4': ["no username test_user", "no username bill"],
    'd_test_5': ["no username test_user"],
    'd_test_6': ["no username bill"],
    'd_test_7': ["no username test_user"],
    'o_test_1': ["no username tonyp", "no username bill", "no username test_user"],
    'o_test_2': ["username new_user privilege 12 password 8 $5$r/Rkdu1jWlkfA6Tc$xITDzzMLOs2ASvQJAWxfPMLN8RlydylygGl1BOfse2B",
                 "no username tonyp", "no username bill", "no username test_user"],
    'o_test_3': ["username bill privilege 12 password 8 $5$cCnIE9np5yJ7PjSn$/Ec1wipIQI..kzK0O4CPJyTYW8mMpZL82rUyNjbSu76",
                 "no username tonyp", "no username test_user"],
    'o_test_4': []
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
    op = run_playbook('test_awplus_user.yml', 'test_init')
    pop = parse_output(op)
    op = run_playbook('test_awplus_user.yml', test_name)
    pop = parse_output(op, test_name)
    return check_list(pop, tests[test_name], debug=debug)


def test_merge_empty_config():
    assert run_a_test('m_test_1')


def test_merge_user_no_config():
    assert run_a_test('m_test_2')


def test_merge_add_new_user():
    assert run_a_test('m_test_3', True)


def test_merge_add_user_with_hashed_password():
    assert run_a_test('m_test_4')


def test_merge_add_user_no_password():
    assert run_a_test('m_test_5')


def test_merge_add_user_no_privilege():
    assert run_a_test('m_test_6')


def test_merge_add_user_supply_both_password_types():
    assert run_a_test('m_test_7')


def test_merge_user_supply_both_password_types():
    assert run_a_test('m_test_8')


def test_merge_configured_user_new_password():
    assert run_a_test('m_test_9')


def test_merge_configured_user_new_privilege():
    assert run_a_test('m_test_10')


def test_merge_switch_password_types():
    assert run_a_test('m_test_11')


def test_merge_users_privilege_password_to_0():
    assert run_a_test('m_test_12')


def test_merge_new_user_privilege_password_set_to_0():
    assert run_a_test('m_test_13')


def test_merge_add_user_privilege_set_to_0():
    assert run_a_test('m_test_14')


def test_merge_change_password_from_MD5_1():
    assert run_a_test('m_test_15')


def test_merge_change_password_from_MD5_2():
    assert run_a_test('m_test_16')


def test_merge_change_password_from_MD5_3():
    assert run_a_test('m_test_17')


def test_merge_10_users():
    assert run_a_test('m_test_18')


def test_merge_idempotency_test():
    assert run_a_test('m_test_19')


def test_replace_users_password():
    assert run_a_test('r_test_1')


def test_replace_users_privilege():
    assert run_a_test('r_test_2')


def test_replace_users_password_with_MD5_hash():
    assert run_a_test('r_test_3')


def test_delete_empty_config():
    assert run_a_test('d_test_1')


def test_delete_non_existent_user():
    assert run_a_test('d_test_2')


def test_delete_user_with_name():
    assert run_a_test('d_test_3')


def test_delete_multiple_users_with_name():
    assert run_a_test('d_test_4')


def test_delete_users_password():
    assert run_a_test('d_test_5')


def test_delete_users_hashed_password():
    assert run_a_test('d_test_6')


def test_delete_users_password_with_wrong_password():
    assert run_a_test('d_test_7')
