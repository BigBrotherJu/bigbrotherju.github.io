# RISC-V Floating Point ABI

## Compatibility between `-march` and `-mabi`

```
-march   -mabi
rv32i    ILP32
rv32if   ILP32 ILP32F
rv32ifd  ILP32 ILP32F ILP32D
rv64i    LP64
rv64if   LP64  LP64F
rv64ifd  LP64  LP64F LP64D
```

- Some requirements

  The D extension depends on the base single-precision instruction subset F.

  The ILP32* ABIs are only compatible with RV32* ISAs, and the LP64* ABIs are only compatible with RV64* ISAs.

  The *F ABIs require the *F ISA extension, the *D ABIs require the *D ISA extension

- `-mabi` 只规定参数传递方式

  `-mabi` 只规定参数传递方式，不规定是否可以使用 F/D extension 寄存器和指令。

  `-mabi` specifies the largest floating-point type that ends up in registers as part of the ABI, but do not control if code generation is allowed to use floating-point internally.

- 编译器根据 `-march` 决定是否使用 F/D extension 寄存器和指令。

## Code Example

```c
float process_data(float input, double multiplier) {
    float result = input * 3.14f;
    result *= multiplier;
    return result;
}
```

### `-march=rv64if -mabi=lp64`

`-mabi=lp64` 只规定了 `input` 和 `multiplier` 都通过整数寄存器传递。

编译器根据 `-march=rv64if` 使用了 F extension 寄存器和指令。

``` console
$ riscv64-linux-gnu-gcc -c -O -march=rv64if -mabi=lp64 riscv-floating.c -o rv64if-lp64
$ riscv64-linux-gnu-objdump -dr --disassembler-color=on rv64if-lp64

rv64if-lp64:     file format elf64-littleriscv


Disassembly of section .text:

0000000000000000 <process_data>:
   0:   ff010113                addi    sp,sp,-16
   4:   00113423                sd      ra,8(sp)
   8:   00813023                sd      s0,0(sp)

   c:   00058413                mv      s0,a1

  # 应该是把 3.14f load 进 fa5
  10:   00000797                auipc   a5,0x0
                        10: R_RISCV_PCREL_HI20  .LC0
                        10: R_RISCV_RELAX       *ABS*
  14:   0007a787                flw     fa5,0(a5) # 10 <process_data+0x10>
                        14: R_RISCV_PCREL_LO12_I        .L0
                        14: R_RISCV_RELAX       *ABS*

  # 把 input load 进 fa4
  18:   f0050753                fmv.w.x fa4,a0

  # fa5 = 3.14f * input
  1c:   10f777d3                fmul.s  fa5,fa4,fa5
  # a0 = 3.14f * input
  20:   e0078553                fmv.x.w a0,fa5

  # 因为 -march=rv64if 没有 d，所以 float -> double 只能调用 __extendsfdf2
  24:   00000097                auipc   ra,0x0
                        24: R_RISCV_CALL_PLT    __extendsfdf2
                        24: R_RISCV_RELAX       *ABS*
  28:   000080e7                jalr    ra # 24 <process_data+0x24>

  # 因为 -march=rv64if 没有 d，所以 double * double 只能调用 __muldf3
  2c:   00040593                mv      a1,s0
  30:   00000097                auipc   ra,0x0
                        30: R_RISCV_CALL_PLT    __muldf3
                        30: R_RISCV_RELAX       *ABS*
  34:   000080e7                jalr    ra # 30 <process_data+0x30>

  # 因为 -march=rv64if 没有 d，所以 double -> float 只能调用 __truncdfsf2
  38:   00000097                auipc   ra,0x0
                        38: R_RISCV_CALL_PLT    __truncdfsf2
                        38: R_RISCV_RELAX       *ABS*
  3c:   000080e7                jalr    ra # 38 <process_data+0x38>

  40:   00813083                ld      ra,8(sp)
  44:   00013403                ld      s0,0(sp)
  48:   01010113                addi    sp,sp,16
  4c:   00008067                ret
```

### `-march=rv64if -mabi=lp64f`

`-mabi=lp64f` 规定了 `float` 类型参数可以通过 F 寄存器传递，`double` 类型参数依然要用整数寄存器传递。

编译器根据 `-march=rv64if` 使用了 F extension 寄存器和指令。

``` console
$ riscv64-linux-gnu-gcc -c -O -march=rv64if -mabi=lp64f riscv-floating.c -o rv64if-lp64f
$ riscv64-linux-gnu-objdump -dr --disassembler-color=on rv64if-lp64f

rv64if-lp64f:     file format elf64-littleriscv


Disassembly of section .text:

0000000000000000 <process_data>:
   0:   ff010113                addi    sp,sp,-16
   4:   00113423                sd      ra,8(sp)
   8:   00813023                sd      s0,0(sp)

   c:   00050413                mv      s0,a0

  # 3.14f load 进 fa5
  10:   00000797                auipc   a5,0x0
                        10: R_RISCV_PCREL_HI20  .LC0
                        10: R_RISCV_RELAX       *ABS*
  14:   0007a787                flw     fa5,0(a5) # 10 <process_data+0x10>
                        14: R_RISCV_PCREL_LO12_I        .L0
                        14: R_RISCV_RELAX       *ABS*

  # input 已经在 fa0 里，直接 fa0 * fa5
  18:   10f57553                fmul.s  fa0,fa0,fa5

  # 因为 -march=rv64if 没有 d，所以 float -> double 只能调用 __extendsfdf2，参数在 fa0 里
  1c:   00000097                auipc   ra,0x0
                        1c: R_RISCV_CALL_PLT    __extendsfdf2
                        1c: R_RISCV_RELAX       *ABS*
  20:   000080e7                jalr    ra # 1c <process_data+0x1c>

  # 因为 -march=rv64if 没有 d，所以 double * double 只能调用 __muldf3，参数在 fa0 a1 里
  24:   00040593                mv      a1,s0
  28:   00000097                auipc   ra,0x0
                        28: R_RISCV_CALL_PLT    __muldf3
                        28: R_RISCV_RELAX       *ABS*
  2c:   000080e7                jalr    ra # 28 <process_data+0x28>

  # 因为 -march=rv64if 没有 d，所以 double -> float 只能调用 __truncdfsf2
  30:   00000097                auipc   ra,0x0
                        30: R_RISCV_CALL_PLT    __truncdfsf2
                        30: R_RISCV_RELAX       *ABS*
  34:   000080e7                jalr    ra # 30 <process_data+0x30>

  # 最后的结果应该在 fa0 里
  38:   00813083                ld      ra,8(sp)
  3c:   00013403                ld      s0,0(sp)
  40:   01010113                addi    sp,sp,16
  44:   00008067                ret
```

### `-march=rv64ifd -mabi=lp64`

`-mabi=lp64` 只规定了 `input` 和 `multiplier` 都通过整数寄存器传递。

编译器根据 `-march=rv64ifd` 使用了 D extension 寄存器和指令。整个程序小很多。

``` console
$ riscv64-linux-gnu-gcc -c -O -march=rv64ifd -mabi=lp64 riscv-floating.c -o rv64ifd-lp64
$ riscv64-linux-gnu-objdump -dr --disassembler-color=on rv64ifd-lp64

rv64ifd-lp64:     file format elf64-littleriscv


Disassembly of section .text:

0000000000000000 <process_data>:
   0:   00000797                auipc   a5,0x0
                        0: R_RISCV_PCREL_HI20   .LC0
                        0: R_RISCV_RELAX        *ABS*
   4:   0007a707                flw     fa4,0(a5) # 0 <process_data>
                        4: R_RISCV_PCREL_LO12_I .L0
                        4: R_RISCV_RELAX        *ABS*
   # a0 里面的是 input
   8:   f00507d3                fmv.w.x fa5,a0

   c:   10e7f7d3                fmul.s  fa5,fa5,fa4

  10:   420787d3                fcvt.d.s        fa5,fa5

  # a1 里面的是 multiplier
  14:   f2058753                fmv.d.x fa4,a1

  18:   12e7f7d3                fmul.d  fa5,fa5,fa4

  1c:   4017f7d3                fcvt.s.d        fa5,fa5

  # 最后把结果放回 a0
  20:   e0078553                fmv.x.w a0,fa5

  24:   00008067                ret
```

### `-march=rv64ifd -mabi=lp64f`

`-mabi=lp64f` 规定了 `float` 类型参数可以通过 F 寄存器传递，`double` 类型参数依然要用整数寄存器传递。

编译器根据 `-march=rv64ifd` 使用了 D extension 寄存器和指令。

``` console
$ riscv64-linux-gnu-gcc -c -O -march=rv64ifd -mabi=lp64f riscv-floating.c -o rv64ifd-lp64f
$ riscv64-linux-gnu-objdump -dr --disassembler-color=on rv64ifd-lp64f

rv64ifd-lp64f:     file format elf64-littleriscv


Disassembly of section .text:

0000000000000000 <process_data>:
   0:   00000797                auipc   a5,0x0
                        0: R_RISCV_PCREL_HI20   .LC0
                        0: R_RISCV_RELAX        *ABS*
   4:   0007a787                flw     fa5,0(a5) # 0 <process_data>
                        4: R_RISCV_PCREL_LO12_I .L0
                        4: R_RISCV_RELAX        *ABS*
   # input 直接在 fa0 里
   8:   10f57553                fmul.s  fa0,fa0,fa5

   c:   42050553                fcvt.d.s        fa0,fa0

   # multiplier 还在 a0 里
  10:   f20507d3                fmv.d.x fa5,a0

  14:   12f57553                fmul.d  fa0,fa0,fa5

  18:   40157553                fcvt.s.d        fa0,fa0

  # 结果在 fa0 里
  1c:   00008067                ret
```

### `-march=rv64ifd -mabi=lp64d`

`-mabi=lp64d` 规定了 `float` 类型参数和 `double` 类型参数都可以通过 F 寄存器传递。

编译器根据 `-march=rv64ifd` 使用了 D extension 寄存器和指令。

``` console
$ riscv64-linux-gnu-gcc -c -O -march=rv64ifd -mabi=lp64d riscv-floating.c -o rv64ifd-lp64d
$ riscv64-linux-gnu-objdump -dr --disassembler-color=on rv64ifd-lp64d

rv64ifd-lp64d:     file format elf64-littleriscv


Disassembly of section .text:

0000000000000000 <process_data>:
   0:   00000797                auipc   a5,0x0
                        0: R_RISCV_PCREL_HI20   .LC0
                        0: R_RISCV_RELAX        *ABS*
   4:   0007a787                flw     fa5,0(a5) # 0 <process_data>
                        4: R_RISCV_PCREL_LO12_I .L0
                        4: R_RISCV_RELAX        *ABS*
   # input 在 fa0 里
   8:   10f57553                fmul.s  fa0,fa0,fa5

   c:   42050553                fcvt.d.s        fa0,fa0

   # multiplier 在 fa1 里
  10:   12b57553                fmul.d  fa0,fa0,fa1

  14:   40157553                fcvt.s.d        fa0,fa0

  # 结果在 fa0 里
  18:   00008067                ret
```
