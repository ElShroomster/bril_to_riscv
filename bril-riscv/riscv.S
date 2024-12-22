# Function: ack
.ack:
sw x1, -4(x2)
addi x2, x2, -40
addi x18, x0, 0
sw x18, 28(x2)
addi x18, x0, 1
sw x18, 12(x2)
lw x19, 40(x2)
lw x20, 28(x2)
beq x19, x20, .eq_0
addi x18, x0, 0
jal x0, .exit_cond_0
.eq_0:
addi x18, x0, 1
.exit_cond_0:
sw x18, 32(x2)
lw x19, 32(x2)
beq x19, x0, .m_nonzero
jal x0, .m_zero
.m_zero:
lw x19, 44(x2)
lw x20, 12(x2)
add x18, x19, x20
sw x18, 4(x2)
jalr x0, x1, 0
.m_nonzero:
lw x19, 44(x2)
lw x20, 28(x2)
beq x19, x20, .eq_1
addi x18, x0, 0
jal x0, .exit_cond_1
.eq_1:
addi x18, x0, 1
.exit_cond_1:
sw x18, 20(x2)
lw x19, 20(x2)
beq x19, x0, .n_nonzero
jal x0, .n_zero
.n_zero:
lw x19, 40(x2)
lw x20, 12(x2)
sub x18, x19, x20
sw x18, 8(x2)
# Caller setup
sw x18, -4(x2)
sw x18, -8(x2)
addi x2, x2, -8
jal x1, .ack
lw x18, 0(x2)
addi x2, x2, 12
sw x18, 4(x2)
jalr x0, x1, 0
.n_nonzero:
lw x19, 40(x2)
lw x20, 12(x2)
sub x18, x19, x20
sw x18, 8(x2)
lw x19, 44(x2)
lw x20, 12(x2)
sub x18, x19, x20
sw x18, 16(x2)
# Caller setup
sw x18, -4(x2)
sw x18, -8(x2)
addi x2, x2, -8
jal x1, .ack
lw x18, 0(x2)
addi x2, x2, 12
sw x18, 24(x2)
# Caller setup
sw x18, -4(x2)
sw x18, -8(x2)
addi x2, x2, -8
jal x1, .ack
lw x18, 0(x2)
addi x2, x2, 12
sw x18, 0(x2)
jalr x0, x1, 0
lw x1, 36(x2)
addi x2, x2, 40
# Function: main
.main:
sw x1, -4(x2)
addi x2, x2, -8
# Caller setup
sw x18, -4(x2)
sw x18, -8(x2)
addi x2, x2, -8
jal x1, .ack
lw x18, 0(x2)
addi x2, x2, 12
sw x18, 0(x2)
lw x10, 0(x2)
li x17, 1
ecall
lw x1, 4(x2)
addi x2, x2, 8
