# Function: main
.main:
# Arguments to main
  addi x2, x2, -8
  addi x18, x0, 720
  sw x18, 0(x2)
  addi x18, x0, 844
  sw x18, 4(x2)

  addi x2, x2, -28
  sw x1, 0(x2)

  addi x18, x0, 0
  sw x18, 4(x2)
  lw x19, 32(x2)
  sw x19, 8(x2)
  lw x19, 28(x2)
  sw x19, 12(x2)
.cmp.val:
  lw x19, 8(x2)
  lw x20, 12(x2)
  blt x19, x20, .lt_0
  addi x18, x0, 0
  jal x0, .exit_cond_0
.lt_0:
  addi x18, x0, 1
.exit_cond_0:
  sw x18, 16(x2)
  lw x19, 16(x2)
  beq x19, x0, .else.1
  jal x0, .if.1
.if.1:
  lw x19, 12(x2)
  lw x20, 8(x2)
  sub x18, x19, x20
  sw x18, 20(x2)
  jal x0, .loop.bound
.else.1:
  lw x19, 8(x2)
  lw x20, 12(x2)
  sub x18, x19, x20
  sw x18, 20(x2)
  jal x0, .loop.bound
.loop.bound:
  lw x19, 20(x2)
  lw x20, 4(x2)
  beq x19, x20, .eq_1
  addi x18, x0, 0
  jal x0, .exit_cond_1
.eq_1:
  addi x18, x0, 1
.exit_cond_1:
  sw x18, 24(x2)
  lw x19, 24(x2)
  beq x19, x0, .update.val
  jal x0, .program.end
.update.val:
  lw x19, 16(x2)
  beq x19, x0, .else.2
  jal x0, .if.2
.if.2:
  lw x19, 20(x2)
  sw x19, 12(x2)
  jal x0, .cmp.val
.else.2:
  lw x19, 20(x2)
  sw x19, 8(x2)
  jal x0, .cmp.val
.program.end:
  lw x11, 12(x2)
  addi x10, x0, 1
  ecall
  addi x11, x0, '\n'
  addi x10, x0, 11
  ecall
  addi x11, x0, 0
  addi x10, x0, 17
  ecall
