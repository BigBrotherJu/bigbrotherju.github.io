# Convention in RISC-V Assembly Programming

## 汇编程序与函数调用

RISC-V 提供了 x0-x31 32 个通用寄存器，x0 的值固定为 0。

如果我们只用写一个没有函数调用的汇编程序，其实我们可以自由使用 x1-x31 寄存器，只要我们能保证程序正确。

但是不使用函数调用是不现实的，原因有两点。一、为了可读性和可维护性，当汇编程序的大小超过一定数目以后，我们需要对程序进行拆分。拆分以后的子程序即为函数，要通过函数调用连接。二、其他程序员或者编译器也会编写或者生成函数，这些函数通过函数调用的方式被调用。

所以在汇编程序中，函数调用是很重要的一个部分。

## 如何在汇编程序中实现函数调用

### ra：跳转指令

首先我们需要跳转指令来跳转进函数体和跳转出函数体。RISC-V 提供了 jal 和 jalr 指令进行跳转。一个具体例子如下：

```
foo:
    insn1
    insn2
    jal ra, imm 或者 jalr ra, reg(imm)
    insn3
    ...

bar:
    ...
    jalr x0, ra(0)
```

jal 的 format 为 `jalr rd, imm`，jalr 的 format 为 `jalr rd, rs1(imm)`。

跳转目的由 `pc + imm`（jal）或者 `rs1 + imm`（jalr）决定，如果我们想要跳转到 bar，那么 `pc + imm` 或者 `rs1 + imm` 要等于 bar 的地址。

bar 执行完以后，还要回到 foo 继续执行 insn3 以及后续指令，所以我们需要一种方式来记录 insn3 的地址，供 bar 来返回。jal 和 jalr 都提供了 rd field 来记录 jal/jalr 下一条指令的地址，这就是我们需要的返回地址。

因为函数调用很常见，所以 RISC-V 专门分配一个寄存器 ra 来做 jal/jalr 的 rd，存放返回地址。

当 foo 中执行完 jal/jalr 以后，pc 为 bar 的地址，ra 的值为 insn3 的地址。只要 bar 不改变 ra 的值，在 bar 的末尾执行 `jalr x0, ra(0)` 就可以返回到 insn3。使用 x0 是因为我们不需要记录 `jalr x0, ra(0)` 下一条指令的地址。

### a0-a7：参数和返回值

RISC-V 专门分配 a0-a7 来传递参数，a0-a1 来传递返回值。

意思就是说，在 foo 使用 jal/jalr 跳转到 bar 之前，foo 需要把参数准备好，放在 a0-a7 中。进入 bar 以后，bar 可以直接使用 a0-a7 中的参数值。

同理，在 bar 使用 jalr 返回到 foo 之前，bar 需要把返回值放在 a0-a1 中。返回到 foo 以后，foo 可以直接使用 a0-a1 中的返回值。

### sp，s0/fp：栈

栈从高地址向低地址增长，RISC-V 专门分配 sp 来存储栈的最低地址。函数可能需要在栈上存储数据，所以函数的开头会根据需要减少 sp，函数结尾会复原 sp。

用 sp 来索引栈上的数据不是非常方便，所以 RISC-V 另外分配了一个寄存器 fp 来存储每个 stack frame 的顶部。函数的开头会把 fp 的值（上个函数的 stack frame 顶部）保存到栈上，然后把 fp 调整为当前函数的 stack frame 顶部。函数的结尾会进行复原操作。

当然，我们也可以给 gcc `-fomit-frame-pointer`，从而把 fp 当作普通寄存器 s0 来用。

### t0-t6，s0-s11：其他寄存器

上面我们已经介绍了具有特殊用途的寄存器 ra a0-a7 sp s0/fp，还剩寄存器 t0-t6 s0-s11 可供我们自由使用。

现在有一个问题，bar 执行时会改变一些寄存器的值。如果我们想要 call bar 之前某个寄存器里的值在 call bar 之后保持不变，如何实现？

为此，RISC-V 专门规定了 s0-s11 在函数调用前后值是不变的，即 values persist after function calls。意思就是说，在 call bar 之前和之后，s0-s11 的值是一样的。这是怎么实现的呢？

bar 的函数体中如果使用了 s0-s11，那么在 bar 的开头，需要把用到的 s 寄存器保存在栈上，在 bar 的结尾，把保存的 s 寄存器复原，这样 call bar 之前和之后，s0-s11 的值就是一样的。

另外，RISC-V 还规定了 t0-t6 的值 do not persist after function calls。意思就是说，在 call bar 之前和之后，t0-t6 的值可能会变，也可能不变，我们不能认为 t0-t6 的值是不变的。

如果 foo 需要 call bar 之前和之后 t0-t6 的值不变，在 call bar 之前 foo 需要自行把 t0-t6 的值保存在栈上，在 call bar 之后 foo 需要自行把 t0-t6 的值从栈上复原。

> In general we want to avoid the model where we have to save every register we use. Doing so is both burdensome and possibly wasteful because we could end up saving registers that are never changed.
>
> Additionally it would be wasteful to always save values so instead we specify exactly what values to save using s registers.

## Callee-Saved and Caller-Saved Registers

```
register        name          saver
x0              zero
x1              ra            caller
x2              sp            callee
x3              gp
x4              tp
x5-x7, x28-x31  t0-t2, t3-t6  caller
x8              s0/fp         callee
x9, x18-x27     s1, s2-s11    callee
x10-x17         a0-a7         caller
```

### Callee-Saved Registers

本小节给出 callee-saved register 和 caller-saved register 的定义。

Callee-saved registers' value persist after function calls. 即在 caller_func 中，call callee_func 之前和之后 callee-saved 寄存器值是不变的。

对 s0-s11，我们已经讨论过，如果 callee 使用了，那么 callee 开头需要把值保存到栈上，callee 结尾需要把值从栈上复原到寄存器中。所以值不变。

对 sp 和 fp，我们也已经讨论过，它们的值在 call callee_func 前后都是一样的。

所以 sp s0/fp s1-s11 在 call callee_func 之前和之后的值都是不变的，它们都是 callee-saved registers。巧合的是，sp 和 s0-s11 一样，也是 s 开头的。

> [!NOTE]
> 需要注意的是，一个函数可能不是 caller，但一定是 callee，因为一个函数写出来就是为了被调用的。所以每个函数如果用到了 s0-s11，都需要在函数开头保存，函数结尾复原。

### Caller-Saved Registers

Caller-saved registers' value do not persist after function calls. 即在 caller_func 中，call callee_func 之前和之后 caller-saved 寄存器值可能会改变。

对 ra，call callee_func 之前和之后的值一定会变化，因为 call 对应的 jal/jalr 指令会改写 ra 的值。所以 func_a 如果是 caller，即它还 call 其他函数 func_b，那么 func_a（caller）的开头一定要保存 ra 到栈上；如果 func_a 不是 caller，即 func_a 中没有 call func_b，那么 ra 的值不会变，不用保存到栈上。

对 t0-t6，call callee_func 之前和之后的值可能会变，可能不变，跟 callee_func 是否改变 t0-t6 有关。如果 caller_func 需要 t0-t6 在 call callee_func 之前和之后的值不变，caller_func 需要在 call callee_func 之前把 t0-t6 保存到栈上，在 call callee_func 之后把 t0-t6 的值复原。

对 a0-a1，call callee_func 之前和之后的值可能会变，可能不变，跟 callee_func 的参数和返回值有关。

对 a2-a7，考虑 func_a call func_b call func_c。func_b 有八个参数，func_c 也有八个参数。如果 func_b 的后六个实参和 func_c 的后六个实参不一样，那么当返回到 func_a 中执行 insn1 时，a2-a7 的值就会和 call func_b 之前的不一样。

```
func_a:
    <prepare a0-a7>
    call func_b
    insn1

func_b:
    <prepare a0-a7>
    call func_c
    insn2

func_c:
    ...
```

> [!NOTE]
> 但是一般情况下函数的参数不会有那么多，所以有时候编译器会把一些 a 寄存器（比如 a5）当 t 寄存器用。

ra t0-t6 a0-a7‘s value do not persist after function calls，所以它们都是 caller-saved registers。

> [!NOTE]
> 如果一个函数不是 caller，它根本不需要考虑保存 caller-saved regiters。

## Prologue and Epilogue

综上所述，我们总结一下一个汇编函数开头和结尾需要进行的工作。

### Prologue

return address 和 previous fp 永远在一个 stack frame 的最顶端，return address 在 previous fp 上面。

- fp is used

  - decrement sp to make space for (ra), fp/s0, any other saved registers, and local variable
  - (store ra if a function call is made)
  - store any saved registers used, fp/s0 will always be used
  - adjust fp/s0

- fp is not used

  - decrement sp to make space for (ra), any saved registers, and local variable
  - (store ra if a function call is made)
  - store any saved registers used

### Epilogue

- fp is used

  - (load ra if a function call is made)
  - load any saved registers used, fp/s0 will always be used
  - increment sp back to previous state
  - return with ra

- fp is not used

  - (load ra if a function call is made)
  - load any saved registers used
  - increment sp back to previous state
  - return with ra
