import os
import re
import sys
from junit_xml import TestSuite, TestCase

ANSIBLE_FILE = sys.argv[1]
JUNIT_FILE = sys.argv[2]

def make_testcase(task_line, module):
    match_prev_block = re.search(
        r"TASK \[(\w+) : (.*?)\]", 
        task_line
    )
    if match_prev_block:
        task_name = match_prev_block.group(2)

    return TestCase(task_name, module)

def check_failure(outcome_line, block, test_case):
    if "ERROR" in outcome_line:
        for line in block: 
            pattern = r'"msg": "([\w\s]+)"'
            match_obj = re.search(pattern, line)
            if match_obj:
                test_case.add_failure_info(match_obj.group(1))

def check_error(outcome_line, block, test_case, expect_failure):
    # case where task fails when it should not fail
    if "ERROR" in outcome_line and not expect_failure:
        for line in block: 
            pattern = r'"msg": "(.*?)"'
            match_obj = re.search(pattern, line)
            if match_obj:
                test_case.add_error_info(match_obj.group(1))
    # case where task passes when it should fail
    elif "ERROR" not in outcome_line and expect_failure:
        test_case.add_error_info("Test expected to fail but passed.")

def parse_results():
    # parse the result file and make a list of blocks
    # where each block is a list of lines
    blocks = []
    for file in os.listdir(ANSIBLE_FILE):
        with open(f"{ANSIBLE_FILE}/{file}", 'r') as f:
            lines = f.read().splitlines()
            
            current_block = None
            for line in lines:
                if len(line) != 0:
                    if line.startswith("TASK"):
                        if current_block is not None:
                            blocks.append(current_block)
                        current_block = [line]
                    else:
                        if current_block is not None:
                            current_block.append(line)

    # build up a list of junit test cases, and whether they pass/fail
    test_cases = []
    for i, assert_block in enumerate(blocks):
        task_block = blocks[i-1]

        # find the task name and module of the current block
        match_current_block = re.match(r"TASK \[(\w+) : ([\w\s]+)\]*", assert_block[0])
        if match_current_block:
            module, assert_name = match_current_block.group(1, 2)

        # check that we are looking at an assert block
        if "Assert" in assert_name:
            test_case = make_testcase(task_block[0], module)
            test_cases.append(test_case)

            if "Assert failure" in assert_name:
                check_error(task_block[1], task_block, test_case, expect_failure=True)
            else:
                check_error(task_block[1], task_block, test_case, expect_failure=False)

            check_failure(assert_block[1], assert_block, test_case)
    
    ts = TestSuite("Ansible Integration Test Suite", test_cases)
    xml = TestSuite.to_xml_string([ts])
    
    with open(JUNIT_FILE, "w") as f:
        f.write(xml)

if __name__ == "__main__":
    parse_results()
