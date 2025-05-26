---
title: Relocation
date: 2024-09-16 19:00:20 +0800
categories: [Elf]
tags: [elf]
---

```
         assemble          link
assembly -------> object --------> executable
```

## Assemble Process

- 对同一个 translation unit 中存在定义的函数和变量

  也进行下面的步骤

- 对当前 translation unit 中不存在定义的函数和变量

  - 生成的指令中立即数是 0

  - 另外会在 `rela.` section 中生成一个 relocation entry

    - `r_offset`：指令地址

    - `r_info`

      - 低 32/8 位 type of relocation
      - 剩余高位 symbol table index

    - `r_addend`：可以有，也可以没有。如果没有，addend 在指令立即数里面

      > https://bottomupcs.sourceforge.net/csbu/x3735.htm
      >
      > That addend value needs to be stored somewhere. The two solutions are covered by the two forms. In the REL form the addend is actually store in the program code in the place where the fixed up address should be. This means that to fix up the address properly, you need to first read the memory you are about to fix up to get any addend, store that, find the "real" address, add the addend to it and then write it back (over the addend). The RELA format specifies the addend right there in the relocation.
      >
      > The trade offs of each approach should be clear. With REL you need to do an extra memory reference to find the addend before the fixup, but you don't waste space in the binary because you use relocation target memory. With RELA you keep the addend with the relocation, but waste that space in the on disk binary. Most modern systems use RELA relocations.

## Link Process

- 符号解析：将符号的引用与符号的定义建立关联

- 重定位

  - 合并相关目标文件（链接脚本）

  - 确定每个符号的地址

  - 根据 `.rela...` 在指令中填入新地址

    - 先得到符号的地址
    - 再得到 addend
    - 根据 relocation type 的计算公式，计算出结果
    - 对结果进行处理，放入指令的立即数部分

    > https://www.sco.com/developers/gabi/latest/ch4.reloc.html
    >
    > The typical application of an ELF relocation is to determine the referenced symbol value, extract the addend (either from the field to be relocated or from the addend field contained in the relocation record, as appropriate for the type of relocation record), apply the expression implied by the relocation type to the symbol and addend, extract the desired part of the expression result, and place it in the field to be relocated.

- 链接器松弛

## RISC-V Relocation

### 32-bit Absolute Address

| lui     | R_RISCV_HI20   | S + A |
| -       | -              | -     |
| addi/ld | R_RISCV_LO12_I | S + A |
| sd      | R_RISCV_LO12_S | S + A |

### 32-bit PC-Relative Address

| auipc   | R_RISCV_PCREL_HI20   | S + A - P |
| -       | -                    | -         |
| addi/ld | R_RISCV_PCREL_LO12_I | S - P     |
| sd      | R_RISCV_PCREL_LO12_S | S - P     |

### Procedure Calls

| auipc | R_RISCV_CALL_PLT | S + A - P |
| -     | -                | -         |
| jalr  | N/A              | N/A       |

### PC-Relative Jumps and Branches

## RISC-V Relaxation

- jump 指令？？？
