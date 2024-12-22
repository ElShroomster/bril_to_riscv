import json
import sys

label_number = 0

# TODO: Create a state map that maps all local values to positions relative to stack. 
# This means we read from 2 addresses and write to one address on every instruction. 
# To make this faster, I will implement register allocation
import json
import sys

label_number = 0

def load_variable(variable, variables, args, rd):
    index = 0
    if variable in variables:
        index = variables.index(variable)
    else:
        index = len(variables) + 1 + args.index(variable)

    return f"lw {rd}, {index * 4}(x2)"

def store_variable(variable, variables, args, ra1):
    index = 0
    if variable in variables:
        index = variables.index(variable)
    else:
        index = len(variables) + 1 + args.index(variable)

    return f"sw {ra1}, {index * 4}(x2)"

def get_non_argument_variables(function_json):
    if "args" not in function_json:
        function_args = set()
    else:
        function_args = {arg["name"] for arg in function_json["args"]}

    used_variables = set()

    if "instrs" in function_json:
        for instr in function_json["instrs"]:
            if "dest" in instr:
                used_variables.add(instr["dest"])

    non_argument_vars = used_variables - function_args
    return non_argument_vars

def get_argument_variables(function_json):
    if "args" not in function_json:
        return set()
    else:
        return {arg["name"] for arg in function_json["args"]}

def get_label_number():
    global label_number
    temp = label_number
    label_number += 1
    return temp

def func_prologue(variables):
    instrs = f"sw x1, -4(x2)\n"
    instrs += f"addi x2, x2, -{(len(variables) + 1) * 4}"
    return instrs

def func_epilogue(variables):
    instrs = f"lw x1, {len(variables) * 4}(x2)\n"
    instrs += f"addi x2, x2, {(len(variables) + 1) * 4}"
    return instrs

def caller_setup(instr, variables, func_args):
    op = instr.get("op")
    assert(op == "call")

    instrs = "# Caller setup\n"
    num_args = 0
    for _ in instr.get("args"):
        num_args += 1
        instrs += f"sw x18, -{num_args * 4}(x2)\n"
    if num_args:
        instrs += f"addi x2, x2, -{num_args * 4}\n"
    instrs += f"jal x1, .{instr.get('funcs')[0]}\n"

    instr_type = instr.get("type")
    if instr_type:
        dest = instr.get("dest")
        assert(dest)
        instrs += f"lw x18, 0(x2)\n"
        instrs += f"addi x2, x2, {(num_args + 1) * 4}\n"
        instrs += store_variable(dest, variables, func_args, "x18")
    else:
        instrs += f"addi x2, x2, {(num_args + 1) * 4}\n"
    return instrs

def bril_to_riscv(instr, variables, func_args):
    op = instr.get("op")
    dest = instr.get("dest")
    args = instr.get("args", [])
    value = instr.get("value")
    label = instr.get("label")

    if op == "const":
        return (f"addi x18, x0, {value}\n"
                f"{store_variable(dest, variables, func_args, 'x18')}")
    elif op in ["add", "mul", "sub", "div", "and", "or"]:
        operation_map = {
            "add": "add",
            "mul": "mul",
            "sub": "sub",
            "div": "div",
            "and": "and",
            "or": "or"
        }
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"{load_variable(args[1], variables, func_args, 'x20')}\n"
                f"{operation_map[op]} x18, x19, x20\n"
                f"{store_variable(dest, variables, func_args, 'x18')}")
    elif op == "eq":
        exit_label_number = get_label_number()
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"{load_variable(args[1], variables, func_args, 'x20')}\n"
                f"beq x19, x20, .eq_{exit_label_number}\n"
                f"addi x18, x0, 0\n"
                f"jal x0, .exit_cond_{exit_label_number}\n"
                f".eq_{exit_label_number}:\n"
                f"addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"{store_variable(dest, variables, func_args, 'x18')}")
    elif op == "lt":
        exit_label_number = get_label_number()
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"{load_variable(args[1], variables, func_args, 'x20')}\n"
                f"blt x19, x20, .lt_{exit_label_number}\n"
                f"addi x18, x0, 0\n"
                f"jal x0, .exit_cond_{exit_label_number}\n"
                f".lt_{exit_label_number}:\n"
                f"addi x18, x0, 1\n"
                f".exit_cond_{exit_label_number}:\n"
                f"{store_variable(dest, variables, func_args, 'x18')}")
    elif op == "not":
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"xori x18, x19, 1\n"
                f"{store_variable(dest, variables, func_args, 'x18')}")
    elif op == "id":
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"{store_variable(dest, variables, func_args, 'x19')}")
    elif op == "jmp":
        return f"jal x0, .{instr.get('labels')[0]}"
    elif op == "br":
        return (f"{load_variable(args[0], variables, func_args, 'x19')}\n"
                f"beq x19, x0, .{instr.get('labels')[1]}\n"
                f"jal x0, .{instr.get('labels')[0]}")
    elif op == "ret":
        return "jalr x0, x1, 0"
    elif op == "nop":
        return "add x0, x0, x0"
    elif op == "print":
        riscv_code = []
        for arg in args:
            riscv_code.append(f"{load_variable(arg, variables, func_args, 'x10')}")
            riscv_code.append(f"li x17, 1") # Print syscall
            riscv_code.append(f"ecall")
        return "\n".join(riscv_code)
    elif op == "call":
        return caller_setup(instr, variables, func_args)
    elif label:
        return f".{label}:"
    else:
        return f"# Unsupported operation: {op}: {instr}"

def parse_input_json(data):
    if "functions" in data:
        for func in data["functions"]:
            print(f"# Function: {func['name']}")
            print(f".{func['name']}:")

            variables = list(get_non_argument_variables(func))
            args = list(get_argument_variables(func))

            print(func_prologue(variables))

            for instr in func["instrs"]:
                riscv_instr = bril_to_riscv(instr, variables, args)
                print(riscv_instr)

            print(func_epilogue(variables))

try:
    input_json = sys.stdin.read()
    data = json.loads(input_json)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    exit(1)

parse_input_json(data)