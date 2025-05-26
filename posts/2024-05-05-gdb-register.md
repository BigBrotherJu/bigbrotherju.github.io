---
title: Display GDB Registers Nicely
date: 2024-05-05 17:30:00 +0800
categories: [Debugging]
tags: [gdb, debugging]
---

## Display Registers Normally

- `print $<reg>`

  用 print 命令的时候，没有高级显示。

  用 info 命令的时候，会有高级显示。

- `info registers`

  Print the names and values of all registers except floating-point and vector registers (in the selected stack frame).

- `info all-registers`

  Print the names and values of all registers, including floating-point and vector registers (in the selected stack frame).

- `info registers reggroup …`

  Print the name and value of the registers in each of the specified reggroups.

  The reggroup can be any of those returned by `maint print reggroups` (see Maintenance Commands).

- `info registers regname …`

  Print the relativized value of each specified register regname.

  As discussed in detail below, register values are normally relative to the selected stack frame.

  The regname may be any register name valid on the machine you are using, with or without the initial ‘$’.

## GDB 如何实现高级显示

高级显示即在显示寄存器的值的同时，显示寄存器的各个位域，对 CSR 尤其有用。

据我推测，应该有两种方法。一种是通过 target description，一种是 gdb 内部的自带函数。

- gdb 内部自带函数

  如果没有指定第三方的 target description，一般的 target description 里不会有寄存器的位域信息。但是 `info all-registers` 时有些寄存器仍然会显示出位域信息，比如 RISC-V 的 mstatus 寄存器。

  这应该是 gdb 内部函数 `gdb/riscv-tdep.c:riscv_print_one_register_info` 实现的。这个函数只实现了几个 CSR 的特殊显示，mstatus 的位域还是错的。

- 通过制定第三方 target description

  target description 简单来讲，就是一个描述 ISA 寄存器的文件。

  我们可以先通过 `maintenance print xml-tdesc <filename>` 获得当前的 target description。

  然后在这个基础上，对想要高级显示的寄存器进行编辑，添加位域信息。

  最后，`set tdesc filename <filename>` 使用这个第三方 target description。

  相关命令还有 `unset tdesc filename` `show tdesc filename`。

## 如何编辑 Target Description

对每个位域只有 1 位的寄存器来说，flags 加 bool 最完美。
