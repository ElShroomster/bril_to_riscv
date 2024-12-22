import json
import sys

# Pass arguments to main function 
"""
addi x2, x2, -8\naddi x18, x0, 4\nsw x18, 0(x2)\naddi x18, x0, 20\nsw x18, 4(x2)\n
"""

label_number = 0

def query_arguments():
    inputs = sys.argv[1:]
    # while True:
    #     user_input = input()
    #     if user_input.strip() == "":
    #         break
    #     try:
    #         number = int(user_input)
    #         inputs.append(number)
    #     except ValueError:
    #         pass

    stack_pointer = len(inputs)
    print("# Arguments to main")
    print(f"  addi x2, x2, -{stack_pointer * 4}")

    num_args = 0
    for arg in inputs:
        print(f"  addi x18, x0, {arg}")
        print(f"  sw x18, {num_args * 4}(x2)")
        num_args += 1

    print("")

def load_variable(variable, variables, args, rd, off = 0):
    index = 0
    if variable in variables:
        index = variables.index(variable) + 1 + off
    else:
        index = len(variables) + 1 + args[::-1].index(variable) + off

    # print(f"# Variable {variable} at index {index}")
    return f"lw {rd}, {index * 4}(x2)"

def store_variable(variable, variables, args, ra1):
    index = 0
    if variable in variables:
        index = variables.index(variable) + 1
    else:
        index = len(variables) + 1 + args[::-1].index(variable)

    # print(f"# Variable {variable} at index {index}")
    return f"sw {ra1}, {index * 4}(x2)"

def get_non_argument_variables(function_json):
    if "args" not in function_json:
        function_args = []
    else:
        function_args = get_argument_variables(function_json)

    used_variables = []

    if "instrs" in function_json:
        for instr in function_json["instrs"]:
            if "dest" in instr:
                if instr["dest"] not in function_args and instr["dest"] not in used_variables:
                    used_variables.append(instr["dest"])

    return used_variables

def get_argument_variables(function_json):
    if "args" not in function_json:
        return []
    else:
        mylist = []
        for arg in function_json["args"]:
            if arg["name"] not in mylist:
                mylist.append(arg["name"])
        return mylist

def get_label_number():
    global label_number
    temp = label_number
    label_number += 1
    return temp

def func_prologue(variables):
    total_vars = len(variables) + 1
    instrs = f"  addi x2, x2, -{total_vars * 4}\n"
    instrs += f"  sw x1, 0(x2)\n"
    return instrs

def func_epilogue(variables):
    total_vars = len(variables) + 1
    instrs = f"  lw x1, 0(x2)\n"
    instrs += f"  addi x2, x2, {total_vars * 4}\n"
    return instrs

def caller_setup(instr, variables, func_args):
    op = instr.get("op")
    assert(op == "call")

    instrs = ""
    tot_num_args = len(instr.get("args"))

    if tot_num_args:
        instrs += f"  addi x2, x2, -{tot_num_args * 4}\n"

    num_args = 0
    for arg in instr.get("args"):
        instrs += f"  {load_variable(arg, variables, func_args, 'x18', off = tot_num_args)}\n"
        instrs += f"  sw x18, {num_args * 4}(x2)\n"
        num_args += 1

    instrs += f"  jal x1, .{instr.get('funcs')[0]}\n"

    dest = instr.get("dest")
    if dest:
        instrs += f"  addi x2, x2, {num_args * 4}\n"
        instrs += f"  {store_variable(dest, variables, func_args, "x10")}"
    else:
        instrs += f"  addi x2, x2, {num_args * 4}\n"
    return instrs

def bril_to_riscv(instr, variables, func_args):
    op = instr.get("op")
    dest = instr.get("dest")
    args = instr.get("args", [])
    value = instr.get("value")
    label = instr.get("label")

    if op == "const":
        if value == True:
            return (f"  addi x18, x0, 1\n"
                    f"  {store_variable(dest, variables, func_args, 'x18')}")
        elif value == False:
            return (f"  addi x18, x0, 0\n"
                    f"  {store_variable(dest, variables, func_args, 'x18')}")
        else:
            return (f"  addi x18, x0, {value}\n"
                    f"  {store_variable(dest, variables, func_args, 'x18')}")
    elif op in ["add", "mul", "sub", "div", "and", "or"]:
        operation_map = {
            "add": "add",
            "mul": "mul",
            "sub": "sub",
            "div": "div",
            "and": "and",
            "or": "or"
        }
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  {operation_map[op]} x18, x19, x20\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")
    elif op == "eq":
        exit_label_number = get_label_number()
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  beq x19, x20, .eq_{exit_label_number}\n"
                f"  addi x18, x0, 0\n"
                f"  jal x0, .exit_cond_{exit_label_number}\n"
                f".eq_{exit_label_number}:\n"
                f"  addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")
    elif op == "lt":
        exit_label_number = get_label_number()
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  blt x19, x20, .lt_{exit_label_number}\n"
                f"  addi x18, x0, 0\n"
                f"  jal x0, .exit_cond_{exit_label_number}\n"
                f".lt_{exit_label_number}:\n"
                f"  addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")

    elif op == "gt":
        exit_label_number = get_label_number()
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  blt x20, x19, .gt_{exit_label_number}\n"
                f"  addi x18, x0, 0\n"
                f"  jal x0, .exit_cond_{exit_label_number}\n"
                f".gt_{exit_label_number}:\n"
                f"  addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")

    elif op == "le":
        exit_label_number = get_label_number()
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  bge x20, x19, .le_{exit_label_number}\n"
                f"  addi x18, x0, 0\n"
                f"  jal x0, .exit_cond_{exit_label_number}\n"
                f".le_{exit_label_number}:\n"
                f"  addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")

    elif op == "ge":
        exit_label_number = get_label_number()
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {load_variable(args[1], variables, func_args, 'x20')}\n"
                f"  bge x19, x20, .ge_{exit_label_number}\n"
                f"  addi x18, x0, 0\n"
                f"  jal x0, .exit_cond_{exit_label_number}\n"
                f".ge_{exit_label_number}:\n"
                f"  addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")
    elif op == "not":
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  xori x18, x19, 1\n"
                f"  {store_variable(dest, variables, func_args, 'x18')}")
    elif op == "id":
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  {store_variable(dest, variables, func_args, 'x19')}")
    elif op == "jmp":
        return f"  jal x0, .{instr.get('labels')[0]}"
    elif op == "br":
        return (f"  {load_variable(args[0], variables, func_args, 'x19')}\n"
                f"  beq x19, x0, .{instr.get('labels')[1]}\n"
                f"  jal x0, .{instr.get('labels')[0]}")
    elif op == "ret":
        all_str = ""
        if args:
            all_str += f"  {load_variable(args[0], variables, func_args, 'x10')}\n"
        else:
            all_str += f"  addi x10, x0, 0\n"
        all_str += func_epilogue(variables)
        return all_str + "  jalr x0, x1, 0"
    elif op == "nop":
        return "  add x0, x0, x0"
    elif op == "print":
        riscv_code = []
        for arg in args:
            riscv_code.append(f"  {load_variable(arg, variables, func_args, 'x11')}")
            riscv_code.append(f"  addi x10, x0, 1")  # Print syscall
            riscv_code.append(f"  ecall")
        riscv_code.append(f"  addi x11, x0, '\\n'")
        riscv_code.append(f"  addi x10, x0, 11")  # Print syscall for characters
        riscv_code.append(f"  ecall")
        return "\n".join(riscv_code)
    elif op == "call":
        return caller_setup(instr, variables, func_args)
    elif label:
        return f".{label}:"
    else:
        return f"# Unsupported operation: {op}: {instr}"

def print_func(func):
    print(f"# Function: {func['name']}")
    print(f".{func['name']}:")

    variables = list(get_non_argument_variables(func))
    args = list(get_argument_variables(func))

    if func['name'] == 'main':
        query_arguments()

    print(func_prologue(variables))

    for instr in func["instrs"]:
        riscv_instr = bril_to_riscv(instr, variables, args)
        print(riscv_instr)

    if func['name'] == 'main':
        riscv_code = []
        riscv_code.append(f"  addi x11, x0, 0")
        riscv_code.append(f"  addi x10, x0, 17")  # exit syscall
        riscv_code.append(f"  ecall")
        print("\n".join(riscv_code))
    else:
        print(func_epilogue(variables))

def parse_input_json(data):
    if "functions" in data:
        for func in data["functions"]:
            if func["name"] == "main":
                print_func(func)
                break

        for func in data["functions"]:
            if func["name"] != "main":
                print_func(func)

try:
    input_json = sys.stdin.read()
    data = json.loads(input_json)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    exit(1)

parse_input_json(data)