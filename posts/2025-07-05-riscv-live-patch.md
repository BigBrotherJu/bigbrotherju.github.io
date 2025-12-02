# Live Patching Instructions in RISC-V Linux Kernel

Kernel Live Patching 就是在 kernel 运行的时候用 store 指令往 text 段的一个或多个指令地址写新指令，最终我们需要当前 hart 或者所有 hart 在这些被写指令地址上能 fetch 到新指令。涉及到的操作概括起来即 memory write 和 instruction fetch。这个描述听起来很简单，但是有很多需要考虑的细节，我们结合具体硬件细节进行考虑。

我们先考虑一条指令和当前 hart 的情况。

## 拥有 L1 icache 和 dcache 的硬件实现场景

我们首先讨论拥有 L1 icache 和 dcache 的硬件实现场景。需要注意，memory write 只和 dcache 以及 memory 交互，dcache 支持 cache read 和 cache write；instruction fetch 只和 icache 以及 memory 交互，icache 只支持 cache read。

- Memory write

  - Cache miss

    被写指令对应的 cache line 大概率不在 dcache 里，store 指令大概率会 cache miss。

    - No-write-allocate

      如果 dcache 是 no-write-allocate，那么被写指令对应的 cache line 不会从 memory 被加载到 dcache 中，新指令内容会直接写到 memory 中。

    - Write-allocate

      如果 dcache 是 write-allocate，那么先把被写指令对应的 cache line 从 memory 加载到 dcache 中，新指令内容写到 cache line 中。

      - Write-through

        如果 dcache 是 write-through，那么每次 cache write 都会更新 memory。新指令内容会被写到 memory 中。

      - Write-back

        如果 dcache 是 write-back，那么只有当 cache line 被 evict（cache line 已经 dirty）的时候，才更新 memory，新指令内容才会被写到 memory 中。

  - Cache hit

    如果被写指令对应的 cache line 在 dcache 里，store 指令会 cache hit，新指令内容会被写到 cache line 中。

    - Write-through

      如果 dcache 是 write-through，那么每次 cache write 都会更新 memory。新指令内容会被写到 memory 中。

    - Write-back

      如果 dcache 是 write-back，那么只有当 cache line 被 evict（cache line 已经 dirty）的时候，才更新 memory，新指令内容才会被写到 memory 中。

  - 总结

    总结来说，在 store 指令执行之后，memory 中被写指令地址中的指令内容更新时间不确定。

- Instruction fetch

  instruction fetch 指 store 指令更改被写指令之后，hart 第一次 fetch 被写指令。

  - Cache miss

    store 指令执行后，hart 第一次 fetch 被写指令时，如果对应的 cache line 不在 icache 中（被写指令是 cache line 开头），那么去 memory 中取来放进 icache 中。

    因为 memory 中被写指令地址中的指令内容更新时间不确定，所以 memory 取来放入 icache 的可能是新指令，可能是旧指令。

    **最后 fetch 的可能是新指令，也可能是旧指令。**

  - Cache hit

    store 指令执行后，hart 第一次 fetch 被写指令时，如果对应的 cache line 在 icache 中，那么 hart 直接从 icache 中 fetch 指令。

    这个 cache line 肯定是因为其他指令或者被写指令 fetch cache miss，从 memory 中取来的放入 icache 的。

    - cache line load 发生在 store 指令之前（store 对 memory 的改变一定不会影响 icache）

      比如下面这个例子，有两个 cache line。store 指令执行完以后，memory 中被写指令地址中的指令内容更新时间不确定。

      但是 memory 中 insn 的内容变化一定不会进入 icache，因为 cache line n 已经在 icache 中。

      **store 后第一次 fetch insn，肯定是旧指令**。如果 store 后想要 fetch 新指令，在 fetch insn 之前，第一，cache line n 必须先被 evict，然后再次从 memory load；第二，memory 中 insn 的内容一定要是新指令。

      ```
      ------ cache line n ----------
      ...
      insn（可以是 cache line 第一条）
      ...
      ------ cache line n + 1 ------
      ...
      store to addr of insn
      jmp to insn
      ...
      ```

    - cache line load 发生在 store 指令之后（store 对 memory 的改变一定会影响 icache）

      比如下面这个例子，有两个 cache line。store 指令执行完以后，memory 中被写指令地址中的指令内容更新时间不确定。

      但是在 cache line n+1 load 进 memory 的时候，memory 中 insn 的内容变化一定会跟着进入 icache。

      但是因为 memory 中被写指令地址中的指令内容更新时间不确定，所以进入 icache 的可能是新指令，也可能是老指令。

      **最后 fetch 的可能是新指令，也可能是旧指令。**

      ```
      ------ cache line n ----------
      ...
      store to addr of insn
      ...
      ------ cache line n + 1 ------
      ...
      insn（不能是 cache line 第一条，否则一定会 cache miss）
      ...
      ```

## 拥有 L1 icache/dcache 和 shared L2 cache 的硬件实现场景

我们再讨论拥有 L1 icache/dcache 和 L2 cache 的硬件实现场景，L2 cache 被所有 hart share。

- Memory write

  - Cache miss

    被写指令对应的 cache line 大概率不在 dcache 里，store 指令大概率会 cache miss。

    - No-write-allocate

      如果 dcache 是 no-write-allocate，那么被写指令对应的 cache line 不会从 L2 cache 被加载到 dcache 中，新指令内容会直接写到 L2 cache 中。

      L2 cache write 可能 miss，可能 hit。根据 L2 cache 的属性不同，处理完 L2 cache write 以后：

      - cache miss
        - （L2 cache no-write-allocate）L2 cache 中没有被写指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定
      - cache hit
        - （L2 cache write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定

    - Write-allocate

      如果 dcache 是 write-allocate，那么先把被写指令对应的 cache line 从 L2 cache 加载到 dcache 中，新指令内容写到 cache line 中。

      L2 cache 中可能没有对应的 cache line，需要从 memory 中加载到 L2 cache。

      - Write-through

        如果 dcache 是 write-through，那么每次 cache write 都会更新 L2 cache。新指令内容会被写到 L2 cache 中。

        L2 cache write 一定 hit。根据 L2 cache 的属性不同，处理完 L2 cache write 以后：

        - （L2 cache write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定

      - Write-back

        如果 dcache 是 write-back，那么只有当 cache line 被 evict（cache line 已经 dirty）的时候，才更新 L2 cache，新指令内容才会被写到 L2 cache 中。

        L2 cache write 一定 hit。根据 L2 cache 的属性不同，处理完 L2 cache write 以后：

        - （L2 cache write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定

        但是 L2 cache write 时间不确定。

  - Cache hit

    如果被写指令对应的 cache line 在 dcache 里，store 指令会 cache hit，新指令内容会被写到 cache line 中。

    - Write-through

      如果 dcache 是 write-through，那么每次 cache write 都会更新 L2 cache。新指令内容会被写到 L2 cache 中。

      L2 cache write 可能 miss，可能 hit。根据 L2 cache 的属性不同，处理完 L2 cache write 以后：

      - cache miss
        - （L2 cache no-write-allocate）L2 cache 中没有被写指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定
      - cache hit
        - （L2 cache write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定

    - Write-back

      如果 dcache 是 write-back，那么只有当 cache line 被 evict（cache line 已经 dirty）的时候，才更新 L2 cache，新指令内容才会被写到 L2 cache 中。

      L2 cache write 可能 miss，可能 hit。根据 L2 cache 的属性不同，处理完 L2 cache write 以后：

      - cache miss
        - （L2 cache no-write-allocate）L2 cache 中没有被写指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-allocate/write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定
      - cache hit
        - （L2 cache write-through）L2 cache 中被写指令地址是新指令，memory 中被写指令地址是新指令
        - （L2 cache write-back）L2 cache 中被写指令地址是新指令，memory 中被写指令更新时间不确定

      而且 L2 cache write 时间不确定。

  - Memory write 对应的所有内存操作是一起做的

    如果 L1 dcache L2 cache memory 的被写指令地址都需要更新为新指令，那么这三个操作是一个不可分割的 transaction。不会出现只更新了 L1 dcache，不更新 L2 cache 的情况。

- Instruction fetch

  instruction fetch 指 store 指令更改被写指令之后，hart 第一次 fetch 被写指令。

  - Cache miss

    store 指令执行后，hart 第一次 fetch 被写指令时，如果对应的 cache line 不在 icache 中（被写指令是 cache line 开头），那么去 L2 cache 中取来放进 icache 中。

    如果 L2 cache 中存在被写指令，指令更新的时间不确定，所以 fetch 到的可能是新指令，也可能是旧指令。

    如果 L2 cache 中不存在被写指令，从 memory 取被写指令，memory 中的被写指令更新的时间不确定，所以 fetch 到的可能是新指令，也可能是旧指令。

    **总结起来，最后 fetch 的可能是新指令，也可能是旧指令。**

  - Cache hit

    cache hit 比较复杂，暂时不分析。

## 如何保证 fetch 新指令：fence.i

根据上两小节的讨论，我们已经知道，在 store 指令更改被写指令后，hart 在被写指令地址第一次 fetch 的，可能是新指令，也可能是旧指令。这是一个很大的问题。如果软件需要 hart fetch 新指令，但是 hart 一直 fetch 的都是旧指令，软件的运行可能会有问题。

如果我们需要 hart 一定 fetch 新指令，现状是实现不了的，我们需要引入新的控制方式，即 `fence.i` 指令。

> FENCE.I instruction that provides explicit synchronization between writes to instruction memory and instruction fetches on the same hart.
>
> Currently, this instruction is the only standard mechanism to ensure that stores visible to a hart will also be visible to its instruction fetches.
>
> The FENCE.I instruction is used to synchronize the instruction and data streams.
>
> RISC-V does not guarantee that stores to instruction memory will be made visible to instruction fetches on a RISC-V hart until that hart executes a FENCE.I instruction.
>
> A FENCE.I instruction ensures that a subsequent instruction fetch on a RISC-V hart will see any previous data stores already visible to the same RISC-V hart.
>
> source: The RISC-V Instruction Set Manual Volume I: Unprivileged ISA Chapter 3

第 4 句话阐述了现在的现状，即 store to instruction memory 可能不会被 instruction fetch 观察到。`fence.i` 提供了一个同步点，在执行 `fence.i` 以后，之后 fetch store 指令更改的指令，一定会 fetch 到新指令。

> [!NOTE]
> 需要注意的是，如果不使用 `fence.i`，当前 hart 也可能会在 store 指令后 fetch 到新指令。拿拥有 L1 icache 和 dcache 的硬件实现举例，如果 dcache 是 no-write-allocate 或者 write-through，新指令内容会写到 memory 中。如果 icache read cache miss，会直接从 memory fetch 新指令。但是如果在其他情况下，就需要用 `fence.i`。
>
> 再举一个没有 cache 的简单硬件实现例子，store 直接把新指令写到 memory，hart 直接从 memory fetch 新指令。但是对其他硬件实现，还是需要 `fence.i`。

## fence.i 的实现方式

### Cache 操作

先拿拥有 L1 icache 和 dcache 的硬件实现场景举例，如果要让当前 hart 在 store 指令和 `fence.i` 指令后 fetch 到新的指令，`fence.i` 起码需要：一、flush 被写指令对应的 dcache line。二、flush 被写指令对应的 icache line。但是因为 `fence.i` 带不了参数，所以只能 flush 整个 dcache 和 icache。

### Flush Pipeline

## 如何让其他 hart 也 fetch 新指令

> FENCE.I does not ensure that other RISC-V harts’ instruction fetches will observe the local hart’s stores in a multiprocessor system.
>
> To make a store to instruction memory visible to all RISC-V harts, the writing hart has to execute a data FENCE before requesting that all remote RISC-V harts execute a FENCE.I.
>
> source: The RISC-V Instruction Set Manual Volume I: Unprivileged ISA Chapter 3

## Patch 两条指令

Patch 两条指令要保证：当前 CPU 不会有问题，其他 CPU 也不会有问题。

下面以 call 指令举例（实际为 auipc 和 jalr 指令）。

### 两条指令的执行不会被打断

如果这两条指令的执行不会被打断，那么我们只需要确保在 memory system 中，要么是旧的 auipc jalr，要么是新的 auipc jalr。这点用 naturally-aligned 的 sd 指令就可以做到。

在当前 hart 和其他 hart 眼中，要么是旧的 auipc jalr，要么是新的 auipc jalr。

### 两条指令的执行被 interrupt 打断

如果一个 kernel task 在 auipc 执行后，jalr 执行前，被 interrupt 打断，在处理 interrupt 的时间中，jalr 被更改了（interrupt handler 一般不进行 live patch，一般是另外一个 hart 进行 patch），kernel task 恢复执行后，旧的 auipc 加新的 jalr 会出问题。

问题的关键是 jalr 被更改了。

```
hart A               hart B

auipc (old)
interrupt handling   patch jalr
jalr  (new)
```

### 两条指令的执行被 preemption 打断

如果一个 kernel task A 在 auipc 执行后，jalr 执行前，被 preempt 了。在 A 重新执行之前，另一个 kernel task B（在同一个 hart 或者不同的 hart 上）可能会 patch 指令。A 恢复执行后，旧的 auipc 加新的 jalr 会出问题。

### 解决思路

- 最优雅的方式，只更改一条指令

  ```
  auipc t0, 0
  ld t0, t0(0)
  jalr
  ```

- 在 auipc jalr 周围加上 disable/enable interrupt

  如果要保存中断状态的话，增加的指令太多了，还有内存操作。

- 修改 kernel preemption，每次被 preempt 的时候，检查当前指令和下条指令，如果是 auipc 和 jalr，模拟执行，返回以后跳过 jalr

## 补充材料：原子性

修改指令的过程中 memory write 和 instruction fetch 的原子性是很重要的，本小节进行讨论。

### Memory Write

#### Memory Write 可能不是原子的

首先，我们需要思考，为什么 memory write 需要是原子的？

如果 memory write 不是原子的，最主要的问题是，在一次 store 对应的多次 memory write 中间，被写指令可能会被 fetch。

举一个简单的例子，我们有一个没有 cache 的简单机器，他的操作如下：

- sw 指令往 insn 地址进行 4 byte memory write，实际上分成两次完成
- 第一次 memory write 更改了 insn 的后两个字节
- interrupt 出现，interrupt handler 中 fetch insn；或者另一个 hart fetch insn

此时被 fetch 的 insn 一半是新的，一半是老的，是非法指令。如果 memory write 是原子的，就没有这个问题。

幸运的是，在 RISC-V 中，只要 store 是 naturally aligned，就是原子的。

> Furthermore, whereas naturally aligned loads and stores are guaranteed to execute atomically, misaligned loads and stores might not, and hence require additional synchronization to ensure atomicity.
>
> source: The RISC-V Instruction Set Manual Volume I: Unprivileged ISA Section 2.6

如上所述，misaligned memory write 原子性得不到保证，但是 naturally aligned 的 store 是原子的。

---

对于整个内存系统来说，memory write 原子性的意思就是，在所有内存层级中（cache 和 memory），

### Instruction Fetch

#### Instruction Fetch 可能不是原子的

在 RISC-V 中，instruction fetch 可能不是原子的。原因可能包括以下几个：

- Instruction Size and Bus Width

  If the size of an instruction is larger than the width of the memory bus, the processor needs to perform multiple memory accesses to fetch a single instruction. For instance, on a system with a 16-bit bus, fetching a 32-bit instruction would require two separate memory reads.

- Cache Line Boundaries

  Instructions can cross cache line boundaries. When this happens, the processor might need to issue two separate cache fills to retrieve the complete instruction.

如果 instruction fetch 不是原子的，那么在一次 instruction fetch 对应的多次 memory read 之间，指令可能被另外一个 hart patch。最后的结果是 fetch 的指令有新的部分也有旧的部分，这样的指令肯定是有问题的。

#### ziccif

ziccif 为 instruction fetch 提供了一定程度的保证。官方文档的解释如下：

> **Ziccif** Main memory regions with both the cacheability and coherence PMAs must support instruction fetch, and any instruction fetches of naturally aligned power-of-2 sizes up to min(ILEN,XLEN) (i.e., 32 bits for RVA23) are atomic.
>
> source: RVA23 Profiles Version 1.0

ILEN 是指硬件实现支持的最大指令长度，目前对 RV32/64 来说都是 32 bits。XLEN 对 RV32 是 32 bits，对 RV64 是 64 bits。所以 min(ILEN,XLEN) 对 RV32/64 都是 32 bits。

所以无论 fetch 16 bits 的指令还是 32 bits 的指令，只要它们是 naturally aligned (address 是 size 的倍数)，fetch 就是原子的。
