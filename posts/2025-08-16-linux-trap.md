# Traps in RISC-V Linux

主要关注中断路径。`CSR_TVEC` 被设置为 `handle_exception`。

## handle_exception

### Enter from Userspace

```
// arch/riscv/kernel/entry.S

// 从 userspace 进入，CSR_SCRATCH 里是 kernel tp

SYM_CODE_START(handle_exception)
	/*
	 * If coming from userspace, preserve the user thread pointer and load
	 * the kernel thread pointer.  If we came from the kernel, the scratch
	 * register will contain 0, and we should continue on the current TP.
	 */

// tp = old CSR_SCRATCH
// CSR_SCRATCH = old tp
	csrrw tp, CSR_SCRATCH, tp

// 从 userspace 进入，tp 现在是 kernel tp，scratch 现在是 user tp

// tp 不是 0，即从 userspace 进入，跳转到 .Lsave_context
	bnez tp, .Lsave_context

...

// tp 现在是 kernel tp，kernel tp 指向 task_struct
.Lsave_context:
// 1. 先把寄存器保存在 kernel stack 最顶上的 pt_regs 中，不然下面没有寄存器可用

// sp 现在是 user sp，先存在 TASK_TI_USER_SP 中
	REG_S sp, TASK_TI_USER_SP(tp)
// sp 现在是 kernel stack
	REG_L sp, TASK_TI_KERNEL_SP(tp)
// 把除了 sp tp 的所有寄存器都存在 kernel stack 上的 pt_regs 中
// user sp 上面已经保存在 TASK_TI_USER_SP 中，现在还不好直接保存，下面再保存
// user tp 现在在 scratch 中，下面再保存
	addi sp, sp, -(PT_SIZE_ON_STACK)
	REG_S x1,  PT_RA(sp)
	REG_S x3,  PT_GP(sp)
	REG_S x5,  PT_T0(sp)
	save_from_x6_to_x31

// 2. 禁用一些功能
	/*
	 * Disable user-mode memory access as it should only be set in the
	 * actual user copy routines.
	 *
	 * Disable the FPU/Vector to detect illegal usage of floating point
	 * or vector in kernel space.
	 */
	li t0, SR_SUM | SR_FS_VS

// 3. 保存 pt_regs 需要的其他寄存器，特别注意 user sp 和 user tp

// user sp 被放在 s0 中
	REG_L s0, TASK_TI_USER_SP(tp)
// 原来的 status 被放在 s1 中，然后 status 中 SUM FS VS 被置 0
	csrrc s1, CSR_STATUS, t0
	csrr s2, CSR_EPC
	csrr s3, CSR_TVAL
	csrr s4, CSR_CAUSE
// user tp 被放在 s5 中
	csrr s5, CSR_SCRATCH
	REG_S s0, PT_SP(sp)
	REG_S s1, PT_STATUS(sp)
	REG_S s2, PT_EPC(sp)
	REG_S s3, PT_BADADDR(sp)
	REG_S s4, PT_CAUSE(sp)
	REG_S s5, PT_TP(sp)

// 到这里，user program 被打断时的所有寄存器状态都被保存了

	/*
	 * Set the scratch register to 0, so that if a recursive exception
	 * occurs, the exception vector knows it came from the kernel
	 */
	csrw CSR_SCRATCH, x0

	/* Load the global pointer */
	load_global_pointer

	/* Load the kernel shadow call stack pointer if coming from userspace */
	scs_load_current_if_task_changed s5

#ifdef CONFIG_RISCV_ISA_V_PREEMPTIVE
	move a0, sp
	call riscv_v_context_nesting_start
#endif
	move a0, sp /* pt_regs */

	/*
	 * MSB of cause differentiates between
	 * interrupts and exceptions
	 */
	bge s4, zero, 1f

	/* Handle interrupts */
	call do_irq
	j ret_from_exception
1:
	/* Handle other exceptions */
	slli t0, s4, RISCV_LGPTR
	la t1, excp_vect_table
	la t2, excp_vect_table_end
	add t0, t1, t0
	/* Check if exception code lies within bounds */
	bgeu t0, t2, 3f
	REG_L t1, 0(t0)
2:	jalr t1
	j ret_from_exception
3:

	la t1, do_trap_unknown
	j 2b
SYM_CODE_END(handle_exception)
ASM_NOKPROBE(handle_exception)
```

### Enter from Kernel

```
// arch/riscv/kernel/entry.S

// 从 kernel 进入，CSR_SCRATCH 里是 0

SYM_CODE_START(handle_exception)
	/*
	 * If coming from userspace, preserve the user thread pointer and load
	 * the kernel thread pointer.  If we came from the kernel, the scratch
	 * register will contain 0, and we should continue on the current TP.
	 */

// tp = old CSR_SCRATCH
// CSR_SCRATCH = old tp
	csrrw tp, CSR_SCRATCH, tp

// 从 kernel 进入，tp 现在是 0，scratch 现在是 kernel tp

// 不跳转
	bnez tp, .Lsave_context

.Lrestore_kernel_tpsp:
// tp 现在是 kernel tp
	csrr tp, CSR_SCRATCH

#ifdef CONFIG_64BIT
	/*
	 * The RISC-V kernel does not eagerly emit a sfence.vma after each
	 * new vmalloc mapping, which may result in exceptions:
	 * - if the uarch caches invalid entries, the new mapping would not be
	 *   observed by the page table walker and an invalidation is needed.
	 * - if the uarch does not cache invalid entries, a reordered access
	 *   could "miss" the new mapping and traps: in that case, we only need
	 *   to retry the access, no sfence.vma is required.
	 */
// 只有 RV64 实现了 lazy TLB flushing for vmalloc
// 直接在这里处理 vmalloc 引起的 exception
// 而不是在后面的 page fault handler 中处理
// 如果确实是 vmalloc 引起的 exception，直接处理并且 sret
	new_vmalloc_check
#endif

// 把被打断的 kernel sp 保存到 TASK_TI_KERNEL_SP
	REG_S sp, TASK_TI_KERNEL_SP(tp)

#ifdef CONFIG_VMAP_STACK
// 计算在栈上保存好 struct pt_regs 以后，sp 的值，看看有没有 overflow
	addi sp, sp, -(PT_SIZE_ON_STACK)
	srli sp, sp, THREAD_SHIFT
	andi sp, sp, 0x1
// 如果有 overflow，直接去 handle_kernel_stack_overflow 处理
	bnez sp, handle_kernel_stack_overflow
// 如果没有 overflow，复原原来的 kernel sp
	REG_L sp, TASK_TI_KERNEL_SP(tp)
#endif

.Lsave_context:
// 把被打断的 kernel sp 保存到 TASK_TI_USER_SP，下面再进行保存
	REG_S sp, TASK_TI_USER_SP(tp)
// sp 现在是 kernel stack
	REG_L sp, TASK_TI_KERNEL_SP(tp)
// 把除了 sp tp 的所有寄存器都存在 kernel stack 上的 pt_regs 中
// kernel sp 上面已经保存在 TASK_TI_USER_SP 中，现在还不好直接保存，下面再保存
// kernel tp 现在就在 tp 中
	addi sp, sp, -(PT_SIZE_ON_STACK)
	REG_S x1,  PT_RA(sp)
	REG_S x3,  PT_GP(sp)
	REG_S x5,  PT_T0(sp)
	save_from_x6_to_x31

// 2. 禁用一些功能
	/*
	 * Disable user-mode memory access as it should only be set in the
	 * actual user copy routines.
	 *
	 * Disable the FPU/Vector to detect illegal usage of floating point
	 * or vector in kernel space.
	 */
	li t0, SR_SUM | SR_FS_VS

// 3. 保存 pt_regs 需要的其他寄存器，特别注意 user sp 和 user tp

// 被打断的 kernel sp 被放在 s0 中
	REG_L s0, TASK_TI_USER_SP(tp)
// 原来的 status 被放在 s1 中，然后 status 中 SUM FS VS 被置 0
	csrrc s1, CSR_STATUS, t0
	csrr s2, CSR_EPC
	csrr s3, CSR_TVAL
	csrr s4, CSR_CAUSE
// 被打断的 kernel tp 被放在 s5 中
	csrr s5, CSR_SCRATCH
	REG_S s0, PT_SP(sp)
	REG_S s1, PT_STATUS(sp)
	REG_S s2, PT_EPC(sp)
	REG_S s3, PT_BADADDR(sp)
	REG_S s4, PT_CAUSE(sp)
	REG_S s5, PT_TP(sp)

	/*
	 * Set the scratch register to 0, so that if a recursive exception
	 * occurs, the exception vector knows it came from the kernel
	 */
	csrw CSR_SCRATCH, x0

	/* Load the global pointer */
	load_global_pointer

	/* Load the kernel shadow call stack pointer if coming from userspace */
	scs_load_current_if_task_changed s5

#ifdef CONFIG_RISCV_ISA_V_PREEMPTIVE
	move a0, sp
	call riscv_v_context_nesting_start
#endif
	move a0, sp /* pt_regs */

	/*
	 * MSB of cause differentiates between
	 * interrupts and exceptions
	 */
	bge s4, zero, 1f

	/* Handle interrupts */
	call do_irq
	j ret_from_exception
1:
	/* Handle other exceptions */
	slli t0, s4, RISCV_LGPTR
	la t1, excp_vect_table
	la t2, excp_vect_table_end
	add t0, t1, t0
	/* Check if exception code lies within bounds */
	bgeu t0, t2, 3f
	REG_L t1, 0(t0)
2:	jalr t1
	j ret_from_exception
3:

	la t1, do_trap_unknown
	j 2b
SYM_CODE_END(handle_exception)
ASM_NOKPROBE(handle_exception)
```

#### 嵌套问题

// TODO

### asm-offsets

根据编译 log，主要有以下两步：

```
# CC      arch/riscv/kernel/asm-offsets.s

set -e; mkdir -p include/generated/;
trap "rm -f include/generated/.tmp_asm-offsets.h" EXIT;
{ echo "#ifndef __ASM_OFFSETS_H__";
  echo "#define __ASM_OFFSETS_H__";
  echo "/*";
  echo " * DO NOT MODIFY.";
  echo " *";
  echo " * This file was generated by Kbuild";
  echo " */";
  echo "";
  sed -ne 's:^[[:space:]]*\.ascii[[:space:]]*"\(.*\)".*:\1:; /^->/{s:->#\(.*\):/* \1 */:; s:^->\([^ ]*\) [\$#]*\([^ ]*\) \(.*\):#define \1 \2 /* \3 */:; s:->::; p;}' < arch/riscv/kernel/asm-offsets.s;
  echo "";
  echo "#endif";
} > include/generated/.tmp_asm-offsets.h;
if [ ! -r include/generated/asm-offsets.h ] || ! cmp -s include/generated/asm-offsets.h include/generated/.tmp_asm-offsets.h;
    then:
        '  UPD     include/generated/asm-offsets.h';
        mv -f include/generated/.tmp_asm-offsets.h include/generated/asm-offsets.h;
fi
```

第一步、从 `asm-offsets.c` 生成 `asm-offsets.s`。

`asm-offsets.c` 中只有一个函数 `void asm_offsets(void)`。其中使用宏 `OFFSET` `DEFINE`，比如：

```c
// arch/riscv/kernel/asm-offsets.c

void asm_offsets(void)
{
	OFFSET(TASK_THREAD_RA, task_struct, thread.ra);
	OFFSET(TASK_THREAD_SP, task_struct, thread.sp);
	OFFSET(TASK_THREAD_S0, task_struct, thread.s[0]);
	OFFSET(TASK_THREAD_S1, task_struct, thread.s[1]);
	OFFSET(TASK_THREAD_S2, task_struct, thread.s[2]);
	OFFSET(TASK_THREAD_S3, task_struct, thread.s[3]);
	OFFSET(TASK_THREAD_S4, task_struct, thread.s[4]);
	OFFSET(TASK_THREAD_S5, task_struct, thread.s[5]);
	OFFSET(TASK_THREAD_S6, task_struct, thread.s[6]);
	OFFSET(TASK_THREAD_S7, task_struct, thread.s[7]);
	OFFSET(TASK_THREAD_S8, task_struct, thread.s[8]);
	OFFSET(TASK_THREAD_S9, task_struct, thread.s[9]);
	OFFSET(TASK_THREAD_S10, task_struct, thread.s[10]);
	OFFSET(TASK_THREAD_S11, task_struct, thread.s[11]);
	OFFSET(TASK_THREAD_SUM, task_struct, thread.sum);
	...
	DEFINE(PT_SIZE, sizeof(struct pt_regs));
	...
}
```

这两个宏由 `include/linux/kbuild.h` 提供：

```c
// include/linux/kbuild.h

/* SPDX-License-Identifier: GPL-2.0 */
#ifndef __LINUX_KBUILD_H
#define __LINUX_KBUILD_H

#define DEFINE(sym, val) \
	asm volatile("\n.ascii \"->" #sym " %0 " #val "\"" : : "i" (val))

#define BLANK() asm volatile("\n.ascii \"->\"" : : )

#define OFFSET(sym, str, mem) \
	DEFINE(sym, offsetof(struct str, mem))

#define COMMENT(x) \
	asm volatile("\n.ascii \"->#" x "\"")

#endif
```

最后生成的 `asm-offsets.s` 如下：

```
# arch/riscv/kernel/asm-offsets.s
	.file	"asm-offsets.c"
	.option nopic
	.text
	.align	2
	.globl	asm_offsets
	.type	asm_offsets, @function
asm_offsets:
	addi	sp,sp,-16	#,,
	sd	s0,0(sp)	#,
	sd	ra,8(sp)	#,
	addi	s0,sp,16	#,,

.ascii "->TASK_THREAD_RA 2480 offsetof(struct task_struct, thread.ra)"
.ascii "->TASK_THREAD_SP 2488 offsetof(struct task_struct, thread.sp)"
...
.ascii "->PT_SIZE 288 sizeof(struct pt_regs)"
...
	ld	ra,8(sp)		#,
	ld	s0,0(sp)		#,
	addi	sp,sp,16	#,,
	jr	ra		#
	.size	asm_offsets, .-asm_offsets
	.ident	"GCC: (GNU) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
```

第二步、根据 `arch/riscv/kernel/asm-offsets.s` 生成 `include/generated/asm-offsets.h`。

`asm-offsets.h` 内容如下：

```c
#ifndef __ASM_OFFSETS_H__
#define __ASM_OFFSETS_H__
/*
 * DO NOT MODIFY.
 *
 * This file was generated by Kbuild
 */

#define TASK_THREAD_RA 2480 /* offsetof(struct task_struct, thread.ra) */
#define TASK_THREAD_SP 2488 /* offsetof(struct task_struct, thread.sp) */
...
#define PT_SIZE 288 /* sizeof(struct pt_regs) */
...
#endif
```

## do_irq()

```c
// arch/riscv/kernel/traps.c

asmlinkage void noinstr do_irq(struct pt_regs *regs)
{
	irqentry_state_t state = irqentry_enter(regs);

	if (IS_ENABLED(CONFIG_IRQ_STACKS) && on_thread_stack())
		call_on_irq_stack(regs, handle_riscv_irq);
	else
		handle_riscv_irq(regs);

	irqentry_exit(regs, state);
}
```

### 辅助函数：irqentry_enter()

```c
// kernel/entry/common.c

noinstr irqentry_state_t irqentry_enter(struct pt_regs *regs)
{
	irqentry_state_t ret = {
		.exit_rcu = false,
	};

	if (user_mode(regs)) {
		irqentry_enter_from_user_mode(regs);
		return ret;
	}

	/*
	 * If this entry hit the idle task invoke ct_irq_enter() whether
	 * RCU is watching or not.
	 *
	 * Interrupts can nest when the first interrupt invokes softirq
	 * processing on return which enables interrupts.
	 *
	 * Scheduler ticks in the idle task can mark quiescent state and
	 * terminate a grace period, if and only if the timer interrupt is
	 * not nested into another interrupt.
	 *
	 * Checking for rcu_is_watching() here would prevent the nesting
	 * interrupt to invoke ct_irq_enter(). If that nested interrupt is
	 * the tick then rcu_flavor_sched_clock_irq() would wrongfully
	 * assume that it is the first interrupt and eventually claim
	 * quiescent state and end grace periods prematurely.
	 *
	 * Unconditionally invoke ct_irq_enter() so RCU state stays
	 * consistent.
	 *
	 * TINY_RCU does not support EQS, so let the compiler eliminate
	 * this part when enabled.
	 */
	if (!IS_ENABLED(CONFIG_TINY_RCU) && is_idle_task(current)) {
		/*
		 * If RCU is not watching then the same careful
		 * sequence vs. lockdep and tracing is required
		 * as in irqentry_enter_from_user_mode().
		 */
		lockdep_hardirqs_off(CALLER_ADDR0);
		// inform RCU that current CPU is entering irq away from idle
		ct_irq_enter();
		instrumentation_begin();
		kmsan_unpoison_entry_regs(regs);
		trace_hardirqs_off_finish();
		instrumentation_end();

		ret.exit_rcu = true;
		return ret;
	}

	/*
	 * If RCU is watching then RCU only wants to check whether it needs
	 * to restart the tick in NOHZ mode. rcu_irq_enter_check_tick()
	 * already contains a warning when RCU is not watching, so no point
	 * in having another one here.
	 */
	lockdep_hardirqs_off(CALLER_ADDR0);
	instrumentation_begin();
	kmsan_unpoison_entry_regs(regs);
	// RCU only wants to check whether it needs to restart
	// the tick in NOHZ mode
	rcu_irq_enter_check_tick();
	trace_hardirqs_off_finish();
	instrumentation_end();

	return ret;
}
```

#### 辅助函数：irqentry_enter_from_user_mode()

```c
// kernel/entry/common.c

noinstr void irqentry_enter_from_user_mode(struct pt_regs *regs)
{
	enter_from_user_mode(regs);
}

// include/linux/entry-common.h

/**
 * enter_from_user_mode - Establish state when coming from user mode
 *
 * Syscall/interrupt entry disables interrupts, but user mode is traced as
 * interrupts enabled. Also with NO_HZ_FULL RCU might be idle.
 *
 * 1) Tell lockdep that interrupts are disabled
 * 2) Invoke context tracking if enabled to reactivate RCU
 * 3) Trace interrupts off state
 *
 * Invoked from architecture specific syscall entry code with interrupts
 * disabled. The calling code has to be non-instrumentable. When the
 * function returns all state is correct and interrupts are still
 * disabled. The subsequent functions can be instrumented.
 *
 * This is invoked when there is architecture specific functionality to be
 * done between establishing state and enabling interrupts. The caller must
 * enable interrupts before invoking syscall_enter_from_user_mode_work().
 */
// enter_from_user_mode is a critical, low-level helper function that
// performs the initial housekeeping and state setup required whenever
// the CPU transitions from user mode to kernel mode
// (due to a system call, page fault, or other exception).
static __always_inline void enter_from_user_mode(struct pt_regs *regs)
{
	// riscv 没实现，arch_enter_from_user_mode 是空的
	arch_enter_from_user_mode(regs);
	// CONFIG_PROVE_LOCKING 为 0，lockdep_hardirqs_off 为空
	// CONFIG_PROVE_LOCKING 主要是从数学形式上证明锁的正确性，防止死锁
	// lockdep_hardirqs_off explicitly tells the lockdep debugging
	// system that hardware interrupts are now disabled.
	lockdep_hardirqs_off(CALLER_ADDR0);

	// CONFIG_CONTEXT_TRACKING_USER 为 0，CT_WARN_ON user_exit_irqoff 为空
	// CONFIG_CONTEXT_TRACKING_USER tracks transitions between kernel
	// and user on behalf of RCU and tickless cputime accounting.
	// The former case relies on context tracking to enter/exit
	// RCU extended quiescent states.
	CT_WARN_ON(__ct_state() != CT_STATE_USER);
	// This informs the context tracking system that the CPU is
	// no longer running user-space code.
	// This is particularly important for RCU
	user_exit_irqoff();

	// CONFIG_NOINSTR_VALIDATION 为 0，instrumentation_begin 为空
	instrumentation_begin();
	// When the kernel enters from user space
	// (e.g., via a system call), the data in the CPU registers
	// is coming from an external source.
	// KMSAN treats this data as initialized to prevent
	// false bug reports.
	kmsan_unpoison_entry_regs(regs);
	// notifies the kernel's tracing infrastructure (ftrace, perf)
	// that the "interrupts off" event is complete.
	// This allows tracing tools to accurately measure the time
	// spent with interrupts disabled during kernel entry.
	trace_hardirqs_off_finish();
	// CONFIG_NOINSTR_VALIDATION 为 0，instrumentation_end 为空
	instrumentation_end();
}
```

### 辅助函数：on_thread_stack()

Its primary purpose is to answer the question: "Is the current stack pointer (sp) located within the memory region allocated for the current process's kernel stack?"

This is crucial in contexts like interrupt handling. If an interrupt occurs, the kernel needs to know if it's running on the regular task stack (which might be nearly full) or if it's already on a special-purpose stack (like an IRQ stack).

原理：内核栈的大小是 16 KB，从上到下增长。假设当前 task 的 stack 基地址为 0xffff ffff 8100 4000，这个 stack 的范围一直到 0xffff ffff 8100 0000。只要当前 sp 在这个 stack 的范围中，sp 低 14 位可以随便变化，但是高 50 位一定是一样的。

如果当前 sp 在这个 stack 的范围中，current->stack ^ current_stack_pointer 结果高 50 位一定为 0。`~(THREAD_SIZE - 1)` 高 50 位为 1，低 14 位为 0。两个结果 and，结果为 0。

如果当前 sp 不在这个 stack 的范围中，current->stack ^ current_stack_pointer 结果高 50 位一定不为 0。`~(THREAD_SIZE - 1)` 高 50 位为 1，低 14 位为 0。两个结果 and，结果不为 0。

```c
// arch/riscv/include/asm/stacktrace.h

static inline bool on_thread_stack(void)
{
	// current_stack_pointer is the value of sp
	// THREAD_SIZE is the total size of kernel stack
	return !(((unsigned long)(current->stack) ^ current_stack_pointer) & ~(THREAD_SIZE - 1));
}
```

### 辅助函数：call_on_irq_stack()

```
// arch/riscv/kernel/entry.S

#ifdef CONFIG_IRQ_STACKS
/*
 * void call_on_irq_stack(struct pt_regs *regs,
 * 		          void (*func)(struct pt_regs *));
 *
 * Calls func(regs) using the per-CPU IRQ stack.
 */
SYM_FUNC_START(call_on_irq_stack)
	/* Create a frame record to save ra and s0 (fp) */
	// 这时操作的还是 kernel stack
	addi	sp, sp, -STACKFRAME_SIZE_ON_STACK
	REG_S	ra, STACKFRAME_RA(sp)
	REG_S	s0, STACKFRAME_FP(sp)
	addi	s0, sp, STACKFRAME_SIZE_ON_STACK

	/* Switch to the per-CPU shadow call stack */
	scs_save_current
	scs_load_irq_stack t0

	/* Switch to the per-CPU IRQ stack and call the handler */
	load_per_cpu t0, irq_stack_ptr, t1 // t0 中最后的值是 irq stack 的基地址
	li	t1, IRQ_STACK_SIZE // irq stack size 也是 16 KB
	add	sp, t0, t1         // sp 现在是 irq stack 的顶层
	jalr	a1                 // 执行 handle_riscv_irq

	// 返回以后，sp 还是 irq stack 的顶层，s0 是执行 handle_riscv_irq 之前的 s0

	/* Switch back to the thread shadow call stack */
	scs_load_current

	/* Switch back to the thread stack and restore ra and s0 */
	addi	sp, s0, -STACKFRAME_SIZE_ON_STACK
	REG_L	ra, STACKFRAME_RA(sp)
	REG_L	s0, STACKFRAME_FP(sp)
	addi	sp, sp, STACKFRAME_SIZE_ON_STACK

	// sp 恢复到了 thread stack

	ret
SYM_FUNC_END(call_on_irq_stack)
#endif /* CONFIG_IRQ_STACKS */
```

#### 辅助函数：load_per_cpu

```
// arch/riscv/include/asm/asm.h

#ifdef CONFIG_SMP
#ifdef CONFIG_32BIT
#define PER_CPU_OFFSET_SHIFT 2
#else
#define PER_CPU_OFFSET_SHIFT 3
#endif

.macro asm_per_cpu dst sym tmp
	REG_L \tmp, TASK_TI_CPU_NUM(tp)
	slli  \tmp, \tmp, PER_CPU_OFFSET_SHIFT
	la    \dst, __per_cpu_offset
	add   \dst, \dst, \tmp
	REG_L \tmp, 0(\dst)
	la    \dst, \sym
	add   \dst, \dst, \tmp
.endm
#else /* CONFIG_SMP */
...
#endif /* CONFIG_SMP */

.macro load_per_cpu dst ptr tmp
	asm_per_cpu \dst \ptr \tmp
	REG_L \dst, 0(\dst)
.endm
```

`load_per_cpu t0, irq_stack_ptr, t1` 展开以后就是：

```
REG_L t1, TASK_TI_CPU_NUM(tp)      // 获得 cpu 数值
slli  t1, t1, PER_CPU_OFFSET_SHIFT // 获得 cpu 数值 * 8（指针大小）
// This array holds the base memory addr for each CPU's private data area
la    t0, __per_cpu_offset
add   t0, t0, t1
REG_L t1, 0(t0) // 从 __per_cpu_offset 中读出当前 CPU 的 per-cpu data 地址
la    t0, irq_stack_ptr
// 现在 t0 是当前 CPU per-cpu data 中，存储 irq_stack_ptr 的 ulong * 的地址
add   t0, t0, t1

REG_L t0, 0(t0) // 获取 irq_stack_ptr 中的值
```

### 辅助函数：handle_riscv_irq()

```c
// arch/riscv/kernel/traps.c

static void noinstr handle_riscv_irq(struct pt_regs *regs)
{
	struct pt_regs *old_regs;

	// irq_enter_rcu is the primary function for entering
	// a hard IRQ context. It disables preemption, notifies the RCU and
	// timekeeping systems, and updates kernel statistics.
	irq_enter_rcu();
	old_regs = set_irq_regs(regs);

	// 现在 old_regs 的值为 __irq_regs 老的值，__irq_regs 更新为 regs

	handle_arch_irq(regs); // 即 drivers/irqchip/irq-riscv-intc.c:riscv_intc_irq
	// 复原 __irq_regs
	set_irq_regs(old_regs);
	irq_exit_rcu();
}
```

#### 辅助函数：irq_enter_rcu()

```c
// kernel/softirq.c

/**
 * irq_enter_rcu - Enter an interrupt context with RCU watching
 */
void irq_enter_rcu(void)
{
	__irq_enter_raw();

	if (tick_nohz_full_cpu(smp_processor_id()) ||
	    (is_idle_task(current) && (irq_count() == HARDIRQ_OFFSET)))
		tick_irq_enter();

	account_hardirq_enter(current);
}

// include/linux/hardirq.h

#define __irq_enter_raw()				\
	do {						\
		preempt_count_add(HARDIRQ_OFFSET);	\
		lockdep_hardirq_enter();		\
	} while (0)
```

#### 辅助函数：set_irq_regs()

```c
// include/asm-generic/irq_regs.h

DECLARE_PER_CPU(struct pt_regs *, __irq_regs);

static inline struct pt_regs *set_irq_regs(struct pt_regs *new_regs)
{
	struct pt_regs *old_regs;

	old_regs = __this_cpu_read(__irq_regs);
	__this_cpu_write(__irq_regs, new_regs);
	return old_regs;
}
```

#### 辅助函数：handle_arch_irq/riscv_intc_irq()

在启动的时候，`drivers/irqchip/irq-riscv-intc.c:riscv_intc_init_common` 调用 `set_handle_irq` 设置 `handle_arch_irq` 为 `drivers/irqchip/irq-riscv-intc.c:riscv_intc_irq`。

```c
// kernel/irq/handle.c

#ifdef CONFIG_GENERIC_IRQ_MULTI_HANDLER

void (*handle_arch_irq)(struct pt_regs *) __ro_after_init;

int __init set_handle_irq(void (*handle_irq)(struct pt_regs *))
{
	if (handle_arch_irq)
		return -EBUSY;

	handle_arch_irq = handle_irq;
	return 0;
}

#endif
```

```c
// drivers/irqchip/irq-riscv-intc.c

static void riscv_intc_irq(struct pt_regs *regs)
{
	unsigned long cause = regs->cause & ~CAUSE_IRQ_FLAG;

	if (generic_handle_domain_irq(intc_domain, cause))
		pr_warn_ratelimited("Failed to handle interrupt (cause: %ld)\n", cause);
}
```

对 `riscv_intc_irq` 的具体讨论见下。

#### 辅助函数：irq_exit_rcu/__irq_exit_rcu()

```c
// kernel/softirq.c

/**
 * irq_exit_rcu() - Exit an interrupt context without updating RCU
 *
 * Also processes softirqs if needed and possible.
 */
void irq_exit_rcu(void)
{
	__irq_exit_rcu();
	 /* must be last! */
	lockdep_hardirq_exit(); // 和上面的 lockdep_hardirq_enter 相对
}

static inline void __irq_exit_rcu(void)
{
#ifndef __ARCH_IRQ_EXIT_IRQS_DISABLED
	local_irq_disable(); // 把 sstatus 的 IE 位置 0 TODO
#else
	lockdep_assert_irqs_disabled();
#endif
	account_hardirq_exit(current); // 和上面的 account_hardirq_enter 相对
	preempt_count_sub(HARDIRQ_OFFSET); // 和上面的 preempt_count_add 相对
	// in_interrupt 检查 preempt_count 的 NMI HARDIRQ SOFTIRQ 位
	// 为什么有 in_interrupt 检查？
	// 因为要检查是否退出了所有中断情况（NMI HARD SOFT)
	// 如果这些位都为 0，意味着我们会返回到一个正常的用户进程中
	// 假设现在 softirq 正在执行，preempt_count 的值为 SOFTIRQ_OFFSET
	// 硬件中断发生，执行 hardirq，preempt_count 的值加上 HARDIRQ_OFFSET
	// hardirq 执行到这一行，preempt_count 的值减去 HARDIRQ_OFFSET
	// 现在 preempt_count 的值非 0，所以 invoke_softirq 不执行
	// 即，如果 hardirq 嵌套在 softirq 中，在这个 hardirq 结束时，不处理 softirq
	if (!in_interrupt() && local_softirq_pending())
		invoke_softirq();

	if (IS_ENABLED(CONFIG_IRQ_FORCED_THREADING) && force_irqthreads() &&
	    local_timers_pending_force_th() && !(in_nmi() | in_hardirq()))
		wake_timersd();

	tick_irq_exit(); // 和上面的 tick_irq_enter 相对
}
```

对 `local_softirq_pending` 和 `invoke_softirq` 的讨论见另一篇文章。

### 辅助函数：irqentry_exit()

```c
// kernel/entry/common.c

noinstr void irqentry_exit(struct pt_regs *regs, irqentry_state_t state)
{
	// This function does not disable interrupts.
	// It asserts that they are already disabled.
	// If interrupts happen to be enabled when this line is executed,
	// lockdep will print a loud warning and a stack trace,
	// effectively crashing the system to highlight a severe bug.
	lockdep_assert_irqs_disabled();

	/* Check whether this returns to user mode */
	if (user_mode(regs)) {
		irqentry_exit_to_user_mode(regs);
	} else if (!regs_irqs_disabled(regs)) {
		// returns to kernel, interrupts are originally on

		/*
		 * If RCU was not watching on entry this needs to be done
		 * carefully and needs the same ordering of lockdep/tracing
		 * and RCU as the return to user mode path.
		 */
		if (state.exit_rcu) {
			instrumentation_begin();
			/* Tell the tracer that IRET will enable interrupts */
			trace_hardirqs_on_prepare();
			lockdep_hardirqs_on_prepare();
			instrumentation_end();
			ct_irq_exit();
			lockdep_hardirqs_on(CALLER_ADDR0);
			return;
		}

		instrumentation_begin();
		if (IS_ENABLED(CONFIG_PREEMPTION))
			irqentry_exit_cond_resched();

		/* Covers both tracing and lockdep */
		trace_hardirqs_on();
		instrumentation_end();
	} else {
		// returns to kernel, interrupts are originally off

		/*
		 * IRQ flags state is correct already. Just tell RCU if it
		 * was not watching on entry.
		 */
		if (state.exit_rcu)
			ct_irq_exit();
	}
}
```

#### 辅助函数：irqentry_exit_to_user_mode()

```c
// kernel/entry/common.c

noinstr void irqentry_exit_to_user_mode(struct pt_regs *regs)
{
	instrumentation_begin();

	// 1) check that interrupts are disabled
	// 2) call tick_nohz_user_enter_prepare()
	// 3) call exit_to_user_mode_loop() if any flags from
	//    EXIT_TO_USER_MODE_WORK are set
	// 4) check that interrupts are still disabled
	exit_to_user_mode_prepare(regs);
	instrumentation_end();
	exit_to_user_mode();
}

// include/linux/entry-common.h

static __always_inline void exit_to_user_mode(void)
{
	instrumentation_begin();
	trace_hardirqs_on_prepare();
	lockdep_hardirqs_on_prepare();
	instrumentation_end();

	// Invoke context tracking if enabled to adjust RCU state
	user_enter_irqoff();
	// Invoke architecture specific last minute exit code,
	// e.g. speculation mitigations, etc. RISC-V doesn't implement this
	arch_exit_to_user_mode();
	// Tell lockdep that interrupts are enabled
	lockdep_hardirqs_on(CALLER_ADDR0);
}
```

## riscv_intc_irq()

