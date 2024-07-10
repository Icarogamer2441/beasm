import sys
import subprocess

macros = []

def comp(code, output):
    tokens = code.split()
    tokenpos = 0
    in_comment = [False]

    compmode = ["elf64"]

    in_label = [False]
    is_macro = [False]

    with open(f"{output}.nasm", "w") as out:
        while tokenpos < len(tokens):
            token = tokens[tokenpos]
            tokenpos += 1

            if not in_label[0] and not in_comment[0]:
                if token.endswith("->"):
                    in_label[0] = True
                    if token == "_nc->":
                        pass
                    else:
                        out.write(f'{token.replace("->", "")}:\n')
                    is_macro[0] = False
                elif token == ".data":
                    out.write(f'section .data\n')
                elif token.endswith(":"):
                    out.write(f'  {token.replace(":", "")} ')
                    while not token.endswith(";"):
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f'{token.replace(":", "").replace(";", "")} ')
                    out.write("\n")
                elif token == ".text":
                    out.write(f'section .text\n')
                elif token == ".bss":
                    out.write(f'section .bss\n')
                elif token == ".64bit":
                    compmode[0] = "elf64"
                elif token == ".32bit":
                    compmode[0] = "elf32"
                elif token == ".bin":
                    compmode[0] = "bin"
                elif token == "glb":
                    token = tokens[tokenpos]
                    tokenpos += 1
                    out.write(f'  global {token}\n')
                elif token.startswith("/*") or token == "/*":
                    in_comment[0] = True
                elif token.startswith("["):
                    out.write(f'{token} ')
                    while not token.endswith("]"):
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f'{token} ')
                    out.write("\n")
                elif token == "@macro":
                    token = tokens[tokenpos]
                    tokenpos += 1
                    macroname = token
                    token = tokens[tokenpos]
                    tokenpos += 1
                    out.write(f"%macro {macroname} {token}\n")
                    macros.append(macroname)
                    in_label[0] = True
                    is_macro[0] = True
                elif token == "@include":
                    token = tokens[tokenpos]
                    tokenpos += 1
                    out.write(f"  %include {token}\n")
            elif in_label[0] and not in_comment[0]:
                if is_macro[0] and token == "@end":
                    out.write(f'%endmacro\n')
                    in_label[0] = False
                elif not is_macro[0] and token == "<-":
                    in_label[0] = False
                else:
                    if token == "move":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        if token == "<-":
                            token = tokens[tokenpos]
                            tokenpos += 1
                            out.write(f"  mov {reg}, {token}\n")
                        else:
                            print("Syntax Error: correct usage: \"move {target} <- {value}\"")
                    elif token == "push":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  push {token}\n")
                    elif token == "pop":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  pop {token}\n")
                    elif token == "compare":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  cmp {reg1}, {token}\n")
                    elif token == "scall":
                        out.write("  syscall\n")
                    elif token == "sum":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  add {reg1}, {token}\n")
                    elif token == "sub":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  sub {reg1}, {token}\n")
                    elif token == "pscall":
                        if compmode[0] == "elf64":
                            out.write("  mov rax, 1\n")
                            out.write("  mov rdi, 1\n")
                            out.write("  pop rsi\n")
                            out.write(f"  pop rdx\n")
                            out.write("  syscall\n")
                        elif compmode[0] == "elf32":
                            out.write("  mov eax, 4\n")
                            out.write("  mov ebx, 1\n")
                            out.write("  pop ecx\n")
                            out.write("  pop edx\n")
                            out.write("  int 0x80\n")
                    elif token == "j==":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  je {token}\n")
                    elif token == "j!=":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jne {token}\n")
                    elif token == "j>":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jg {token}\n")
                    elif token == "j<":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jl {token}\n")
                    elif token == "j>=":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jge {token}\n")
                    elif token == "j<=":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jle {token}\n")
                    elif token == "&&":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  and {reg1}, {token}\n")
                    elif token == "||":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  or {reg1}, {token}\n")
                    elif token == "<<":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  shl {reg1}, {token}\n")
                    elif token == ">>":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  shr {reg1}, {token}\n")
                    elif token == "exit":
                        if compmode[0] == "elf64":
                            out.write(f"  mov rax, 60\n")
                            out.write(f"  pop rdi\n")
                            out.write(f"  syscall\n")
                        elif compmode[0] == "elf32":
                            out.write(f"  mov eax, 1\n")
                            out.write(f"  pop ebx\n")
                            out.write(f"  int 0x80\n")
                    elif token == "int":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  int {token}\n")
                    elif token == "jumpto":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jmp {token}\n")
                    elif token == "x||":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  xor {reg1}, {token}\n")
                    elif token == "call":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  call {token}\n")
                    elif token == "ret":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  ret\n")
                    elif token == "lea":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  lea {reg1}, {token}\n")
                    elif token == "inc":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  inc {token}\n")
                    elif token == "dec":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  dec {token}\n")
                    elif token.startswith("/*") or token == "/*":
                        in_comment[0] = True
                    elif token == "times":
                        out.write(f"  times ")
                        while not token.endswith(";"):
                            token = tokens[tokenpos]
                            tokenpos += 1
                            out.write(f'{token.replace(";", "")} ')
                        out.write("\n")
                    elif token == "db":
                        out.write(f"  db ")
                        while not token.endswith(";"):
                            token = tokens[tokenpos]
                            tokenpos += 1
                            out.write(f'{token.replace(";", "")} 1')
                        out.write(f"\n")
                    elif token == "dw":
                        out.write(f"  dw ")
                        while not token.endswith(";"):
                            token = tokens[tokenpos]
                            tokenpos += 1
                            out.write(f'{token.replace(";", "")} ')
                        out.write(f"\n")
                    elif token == "test":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  test {reg1}, {token}\n")
                    elif token == "j0":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jz {token}\n")
                    elif token == "j1":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  jnz {token}\n")
                    elif token in macros:
                        out.write(f"  {token} ")
                        while not token.endswith(";"):
                            token = tokens[tokenpos]
                            tokenpos += 1
                            out.write(f'{token.replace(";", "")} ')
                        out.write("\n")
                    elif token == "@define":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        name = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  %define {name} {token}\n")
                    elif token == "dup":
                        out.write("  pop rax\n")
                        out.write("  push rax\n")
                        out.write("  push rax\n")
                    elif token == "swap":
                        out.write("  pop rax\n")
                        out.write("  pop rbx\n")
                        out.write("  push rax\n")
                        out.write("  push rbx\n")
                    elif token == "mul":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  imul {reg1}, {token}\n")
                    elif token == "div":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        reg1 = token
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  idiv {reg1}\n")
                    elif token == "loop":
                        token = tokens[tokenpos]
                        tokenpos += 1
                        out.write(f"  loop {token}\n")
            elif in_comment[0]:
                if token.endswith("*/") or token == "*/":
                    in_comment[0] = False
                else:
                    pass
        
    if compmode[0] == "elf32":
        subprocess.run(f"nasm -f {compmode[0]} {output}.nasm -o {output}.o", shell=True)
        subprocess.run(f"ld -m elf_i386 {output}.o -o {output}", shell=True)
        subprocess.run(f"rm -rf {output}.o", shell=True)
    elif compmode[0] == "elf64":
        subprocess.run(f"nasm -f {compmode[0]} {output}.nasm -o {output}.o", shell=True)
        subprocess.run(f"ld -m elf_x86_64 {output}.o -o {output}", shell=True)
        subprocess.run(f"rm -rf {output}.o", shell=True)
    elif compmode[0] == "bin":
        subprocess.run(f"nasm -f {compmode[0]} {output}.nasm -o {output}.bin", shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
    else:
        if sys.argv[1].endswith(".asm") or sys.argv[1].endswith(".beasm") or sys.argv[1].endswith(".s"):
            with open(sys.argv[1], "r") as fi:
                comp(fi.read(), sys.argv[1].replace(".asm", "").replace(".s", "").replace(".beasm", ""))
            if "--asm" in sys.argv:
                pass
            else:
                subprocess.run(f'rm -rf {sys.argv[1].replace(".asm", "").replace(".s", "").replace(".beasm", "")}.nasm', shell=True)
        else:
            print(f"Extension Error: extensions you can use: '.s', '.asm', '.beasm'.")
            sys.exit(1)
