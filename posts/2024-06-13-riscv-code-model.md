---
title: RISC-V Code Model
date: 2024-06-13 17:30:00 +0800
categories: [RISC-V]
tags: [code model, risc-v]
---

RISC-V only has three addressing modes:

- PC-relative, via the `auipc`, `jal` and `br*` instructions.
- Register-offset, via the `jalr`, `addi` and all memory instructions.
- Absolute, via the `lui` instruction (though arguably this is just x0-offset).

## medlow

The program and its statically defined symbols must lie within a single 2 GiB address range and must lie between absolute addresses −2 GiB and +2 GiB. Programs can be statically or dynamically linked.

```
lui a0, xxxx
addi a0, a0, xxxx
```

- 32 位

  `lui`：`R[rd] = { imm, 12'b0 }`

  范围为 `0x0000 0000 - 0xffff f000`。

  `addi`: `R[rd] = R[rs1] + imm(sign-ext)`

  范围为 `0x0000 0000 - 0xffff ffff`。

- 64 位

  `lui`：`R[rd] = { 32b'imm<31>, imm, 12'b0 }`

  `imm<31>` 为 0，范围为 `0x0000 0000 0000 0000 - 0x0000 0000 7fff f000`。

  `imm<31>` 为 1，范围为 `0xffff ffff 8000 0000 - 0xffff ffff ffff f000`。

  `addi`: `R[rd] = R[rs1] + imm(sign-ext)`

  imm 第 11 位为 0，`0x0000 0000 0000 0000 - 0x0000 0000 0000 07ff`。

  imm 第 11 位为 1，`0xffff ffff ffff f800 - 0xffff ffff ffff ffff`。

  最后范围为 `0x0 - 0x000000007FFFF7FF` `0xFFFFFFFF7FFFF800 - 0xFFFFFFFFFFFFFFFF`。

## medany

The program and its statically defined symbols must be within any single 2 GiB address range. Programs can be statically or dynamically linked.

- Function

  ```
          mutex_lock(&nf_conn_btf_access_lock);
  ffffffff80733316:  0017c097  auipc   ra,0x17c
  ffffffff8073331a:  76e080e7  jalr    1902(ra) # ffffffff808afa84 <mutex_lock>
  ```

- Variable

## Reference

https://www.sifive.com/blog/all-aboard-part-4-risc-v-code-models

https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html
