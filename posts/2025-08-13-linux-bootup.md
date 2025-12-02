# RISC-V Linux 启动流程

内核版本为 6.16-rc3，主要关注 stvec 设置、中断相关设置以及 SMP 设置。

## _start

```
ffffffff80000000 <_start>:
ffffffff80000000:       5a4d                    li      s4,-13
ffffffff80000002:       0d60106f                j       ffffffff800010d8 <_start_kernel>
ffffffff80000006:       0001                    nop
```

## config

```
# CONFIG_RISCV_M_MODE not set
# CONFIG_SHADOW_CALL_STACK not set
# CONFIG_RISCV_BOOT_SPINWAIT is not set
# CONFIG_XIP_KERNEL is not set
# CONFIG_BUILTIN_DTB is not set
CONFIG_MMU=y
# CONFIG_KASAN is not set
```

## _start_kernel

_start_kernel 在 call start_kernel 之前，把 stvec 设置为 `handle_exception`。

```
// arch/riscv/kernel/head.S

SYM_CODE_START(_start_kernel)
	/* Mask all interrupts */
	csrw CSR_IE, zero
	csrw CSR_IP, zero

	/* Enable time CSR */
	li t0, 0x2
	csrw CSR_SCOUNTEREN, t0

  	/* Load the global pointer */
	load_global_pointer		// 见下

	/*
	 * Disable FPU & VECTOR to detect illegal usage of
	 * floating point or vector in kernel space
	 */
	li t0, SR_FS_VS
	csrc CSR_STATUS, t0

  	/* Clear BSS for flat non-ELF images */
	la a3, __bss_start
	la a4, __bss_stop
	ble a4, a3, .Lclear_bss_done
.Lclear_bss:
	REG_S zero, (a3)
	add a3, a3, RISCV_SZPTR
	blt a3, a4, .Lclear_bss
.Lclear_bss_done:

	la a2, boot_cpu_hartid
	XIP_FIXUP_OFFSET a2		// 见下
	REG_S a0, (a2)

	/* Initialize page tables and relocate to virtual addresses */
	la tp, init_task
	la sp, init_thread_union + THREAD_SIZE
	XIP_FIXUP_OFFSET sp		// 见下
	addi sp, sp, -PT_SIZE_ON_STACK
	scs_load_init_stack		// 见下

	mv a0, a1

	/* Set trap vector to spin forever to help debug */
	la a3, .Lsecondary_park		// 见下
	csrw CSR_TVEC, a3		// 重点关注，设置 stvec
	call setup_vm

  	la a0, early_pg_dir
	XIP_FIXUP_OFFSET a0		// 见下
	call relocate_enable_mmu

  	call .Lsetup_trap_vector	// 见下
	/* Restore C environment */
	la tp, init_task
	la sp, init_thread_union + THREAD_SIZE
	addi sp, sp, -PT_SIZE_ON_STACK
	scs_load_current		// 见下

  	/* Start the kernel */
	call soc_early_init
	tail start_kernel

SYM_CODE_END(_start_kernel)
```

## _start_kernel 辅助代码

`load_global_pointer`：

```
// arch/riscv/include/asm/asm.h

#ifdef CONFIG_SHADOW_CALL_STACK
/* gp is used as the shadow call stack pointer instead */
.macro load_global_pointer
.endm
#else
/* load __global_pointer to gp */
.macro load_global_pointer
.option push
.option norelax
	la gp, __global_pointer$
.option pop
.endm
#endif /* CONFIG_SHADOW_CALL_STACK */
```

`XIP_FIXUP_OFFSET`：

```
// arch/riscv/include/asm/xip_fixup.h

#ifdef CONFIG_XIP_KERNEL
.macro XIP_FIXUP_OFFSET reg
	/* Fix-up address in Flash into address in RAM early during boot before
	 * MMU is up. Because generated code "thinks" data is in Flash, but it
	 * is actually in RAM (actually data is also in Flash, but Flash is
	 * read-only, thus we need to use the data residing in RAM).
	 *
	 * The start of data in Flash is _sdata and the start of data in RAM is
	 * CONFIG_PHYS_RAM_BASE. So this fix-up essentially does this:
	 * reg += CONFIG_PHYS_RAM_BASE - _start
	 */
	li t0, CONFIG_PHYS_RAM_BASE
        add \reg, \reg, t0
	la t0, _sdata
	sub \reg, \reg, t0
.endm
#else
.macro XIP_FIXUP_OFFSET reg
.endm
#endif /* CONFIG_XIP_KERNEL */
```

`scs_load_init_stack` `scs_load_current`：

```
// arch/riscv/include/asm/scs.h

#ifdef CONFIG_SHADOW_CALL_STACK

/* Load init_shadow_call_stack to gp. */
.macro scs_load_init_stack
	la	gp, init_shadow_call_stack
	XIP_FIXUP_OFFSET gp
.endm

/* Load task_scs_sp(current) to gp. */
.macro scs_load_current
	REG_L	gp, TASK_TI_SCS_SP(tp)
.endm

#else /* CONFIG_SHADOW_CALL_STACK */

.macro scs_load_init_stack
.endm

.macro scs_load_current
.endm

#endif /* CONFIG_SHADOW_CALL_STACK */
```

`.Lsecondary_park`：

```
// arch/riscv/kernel/head.S

.Lsecondary_park:
	/*
	 * Park this hart if we:
	 *  - have too many harts on CONFIG_RISCV_BOOT_SPINWAIT
	 *  - receive an early trap, before setup_trap_vector finished
	 *  - fail in smp_callin(), as a successful one wouldn't return
	 */
	wfi
	j .Lsecondary_park
```

`.Lsetup_trap_vector` 把 stvec 设置成 handle_exception。

```
// arch/riscv/kernel/head.S

.Lsetup_trap_vector:
	/* Set trap vector to exception handler */
	la a0, handle_exception
	csrw CSR_TVEC, a0

	/*
	 * Set sup0 scratch register to 0, indicating to exception vector that
	 * we are presently executing in kernel.
	 */
	csrw CSR_SCRATCH, zero
	ret
```

## start_kernel

```c
// init/main.c

asmlinkage __visible __init __no_sanitize_address __noreturn __no_stack_protector
void start_kernel(void)
{
	...
	setup_arch(&command_line);
	/* Static keys and static calls are needed by LSMs */
	jump_label_init();
	static_call_init();
	...
	trap_init();
	...
	/* init some links before init_ISA_irqs() */
	early_irq_init();
	init_IRQ();
	tick_init();
	rcu_init_nohz();
	timers_init();
	srcu_init();
	hrtimers_init();
	softirq_init();
	timekeeping_init();
	time_init();
	...
	arch_cpu_finalize_init();
	...
	rest_init();
}
```

## start_kernel 辅助函数

### setup_arch

#### setup_arch 函数

```c
// arch/riscv/kernel/setup.c

void __init setup_arch(char **cmdline_p)
{
	parse_dtb();
	setup_initial_init_mm(_stext, _etext, _edata, _end);

	*cmdline_p = boot_command_line;

	early_ioremap_setup();
	sbi_init();
	jump_label_init();
	parse_early_param();

	efi_init();
	paging_init();

	/* Parse the ACPI tables for possible boot-time configuration */
	acpi_boot_table_init();

#if IS_ENABLED(CONFIG_BUILTIN_DTB)
	unflatten_and_copy_device_tree();
#else
	unflatten_device_tree();
#endif
	misc_mem_init();

	init_resources();

#ifdef CONFIG_KASAN
	kasan_init();
#endif

#ifdef CONFIG_SMP
	setup_smp();
#endif

	if (!acpi_disabled) {
		acpi_init_rintc_map();
		acpi_map_cpus_to_nodes();
	}

	riscv_init_cbo_blocksizes();
	riscv_fill_hwcap();
	apply_boot_alternatives();
	init_rt_signal_env();

	if (IS_ENABLED(CONFIG_RISCV_ISA_ZICBOM) &&
	    riscv_isa_extension_available(NULL, ZICBOM))
		riscv_noncoherent_supported();
	riscv_set_dma_cache_alignment();

	riscv_user_isa_enable();
	riscv_spinlock_init();
}
```

#### 辅助函数 parse_dtb（设备树）

`drivers/of/fdt.c:early_init_dt_scan` verifies the DTB header is valid and scans it for basic information like memory layout and the kernel command line. It returns true if a valid DTB was found and processed, and false otherwise.

`drivers/of/fdt.c:of_flat_dt_get_machine_name()` read the machine's name from the DTB. It looks for the `model` or `compatible` property in the root node.

```c
// arch/riscv/kernel/setup.c

static void __init parse_dtb(void)
{
	/* Early scan of device tree from init memory */
	if (early_init_dt_scan(dtb_early_va, dtb_early_pa)) {
		const char *name = of_flat_dt_get_machine_name();

		if (name) {
			pr_info("Machine model: %s\n", name);
			dump_stack_set_arch_desc("%s (DT)", name);
		}
	} else {
		pr_err("No DTB passed to the kernel\n");
	}
}
```

输出：

`[    0.000000] Machine model: riscv-virtio,qemu`

#### 辅助函数 unflatten_device_tree（设备树）

`drivers/of/fdt.c:unflatten_device_tree` unflattens the device-tree passed by the firmware, creating the tree of `struct device_node`. It also fills the "name" and "type" pointers of the nodes so the normal device-tree walking functions can be used.

这一步比较重要，把整个 dtb 转化为内核中的数据结构。

#### 辅助函数 setup_smp（SMP）

```c
// arch/riscv/kernel/smpboot.c

void __init setup_smp(void)
{
	int cpuid;

	cpu_set_ops();	// 把 cpu_ops 设置为 cpu_ops_sbi

	if (acpi_disabled)
  		// 主要在 physical hart id 和 cpuid 之间建立联系
		of_parse_and_init_cpus();
	else
		acpi_parse_and_init_cpus();

        // mark as "possible" targets for subsequent SMP boot-up sequence
	for (cpuid = 1; cpuid < nr_cpu_ids; cpuid++)
		if (cpuid_to_hartid_map(cpuid) != INVALID_HARTID)
			set_cpu_possible(cpuid, true);
}

// arch/riscv/kernel/cpu_ops_sbi.c

const struct cpu_operations cpu_ops_sbi = {
	.cpu_start	= sbi_cpu_start,
#ifdef CONFIG_HOTPLUG_CPU
	.cpu_stop	= sbi_cpu_stop,
	.cpu_is_stopped	= sbi_cpu_is_stopped,
#endif

// arch/riscv/kernel/cpu_ops.c

void __init cpu_set_ops(void)
{
#if IS_ENABLED(CONFIG_RISCV_SBI)
	if (sbi_probe_extension(SBI_EXT_HSM)) {
		pr_info("SBI HSM extension detected\n");
		cpu_ops = &cpu_ops_sbi;
	}
#endif
}
```

### trap_init

RISC-V 没有实现 `trap_init`。

```c
// init/main.c

void __init __weak trap_init(void) { }
```

### early_irq_init

```c
// kernel/irq/irqdesc.c

int __init early_irq_init(void)
{
	int i, initcnt, node = first_online_node;
	struct irq_desc *desc;

	init_irq_default_affinity();	// 默认每个 CPU 都可以处理中断

	/* Let arch update nr_irqs and return the nr of preallocated irqs */
	initcnt = arch_probe_nr_irqs();	// RISC-V 没有实现，默认实现返回 0
	printk(KERN_INFO "NR_IRQS: %d, nr_irqs: %d, preallocated irqs: %d\n",
	       NR_IRQS, nr_irqs, initcnt);

	if (WARN_ON(nr_irqs > MAX_SPARSE_IRQS))
		nr_irqs = MAX_SPARSE_IRQS;

	if (WARN_ON(initcnt > MAX_SPARSE_IRQS))
		initcnt = MAX_SPARSE_IRQS;

	if (initcnt > nr_irqs)
		nr_irqs = initcnt;

	for (i = 0; i < initcnt; i++) {
		desc = alloc_desc(i, node, 0, NULL, NULL);
		irq_insert_desc(i, desc);
	}
	return arch_early_irq_init();	// RISC-V 没有实现，默认实现返回 0
}
```

输出：`[    0.000000] NR_IRQS: 64, nr_irqs: 64, preallocated irqs: 0`

### init_IRQ

#### init_IRQ 函数

注意 `handle_arch_irq` 这个变量和 `set_handle_irq` 这个函数。

```c
// arch/riscv/kernel/irq.c

void __init init_IRQ(void)
{
	init_irq_scs();
	init_irq_stacks();
	irqchip_init(); // irqchip_init 中会设置好 handle_arch_irq
	if (!handle_arch_irq)
		panic("No interrupt controller found.");
	sbi_ipi_init();
}
```

#### 辅助函数 irqchip_init/of_irq_init

```c
// include/linux/mod_devicetable.h

/*
 * Struct used for matching a device
 */
struct of_device_id {
	char	name[32];
	char	type[32];
	char	compatible[128];
	const void *data;
};

// drivers/irqchip/irqchip.c

extern struct of_device_id __irqchip_of_table[];

void __init irqchip_init(void)
{
	of_irq_init(__irqchip_of_table);  // 只有这个函数起作用
	acpi_probe_device_table(irqchip);
}
```

首先，和中断控制器有关的驱动源代码中使用 `IRQCHIP_DECLARE`，定义 `struct of_device_id` 变量，`struct of_device_id` 的 `data` 为初始化函数指针。如：

```c
// drivers/irqchip/irq-riscv-intc.c

IRQCHIP_DECLARE(riscv, "riscv,cpu-intc", riscv_intc_init);

static const struct of_device_id __of_table_riscv
__attribute__(__used__)
__attribute__(__section__("__irqchip_of_table"))
__attribute__((__aligned__(__alignof__(struct of_device_id)))) = {
    .compatible = "riscv,cpu-intc",
    .data = riscv_intc_init
}
```

通过 Kconfig 配置哪些驱动要进行编译。编译好以后的目标文件最后进行链接。我们 enable 的中断控制器驱动中定义的 `struct of_device_id` 最后都会被放到 section `__irqchip_of_table` 中。在链接脚本的帮助下，符号 `__irqchip_of_table` 指向这个 section 的开头。

section `__irqchip_of_table` 会有以下内容：

```
[juhan@arch irqchip]$ pwd
/home/juhan/local/riscv-linux/linux-6.16-rc3/drivers/irqchip
[juhan@arch irqchip]$ ls *.o | sed 's/\.o$/.c/' | xargs grep IRQCHIP_DECLARE
irq-riscv-imsic-early.c:     IRQCHIP_DECLARE(riscv_imsic, "riscv,imsics", imsic_early_dt_init);
irq-riscv-intc.c:            IRQCHIP_DECLARE(riscv, "riscv,cpu-intc", riscv_intc_init);
irq-riscv-intc.c:            IRQCHIP_DECLARE(andes, "andestech,cpu-intc", riscv_intc_init);
irq-sifive-plic.c:           IRQCHIP_DECLARE(riscv, "allwinner,sun20i-d1-plic", plic_early_probe);
irq-thead-c900-aclint-sswi.c:IRQCHIP_DECLARE(thead_aclint_sswi, "thead,c900-aclint-sswi", thead_aclint_sswi_early_probe);
```

`of_irq_init` 首先用 `for_each_matching_node_and_match` 来遍历设备树里的所有 node。对每个 node，这个宏检查 node 的 compatible property 是否和 matches 数组（即 `__irqchip_of_table`）中任一 entry 一样。如果有匹配，执行循环体。QEMU virt machine 设备树中只有以下 node 能匹配上。

```
interrupt-controller {
        #interrupt-cells = <0x01>;
        interrupt-controller;
        compatible = "riscv,cpu-intc";
        phandle = <0x02>;
};
```

循环体先进行一些 sanity check，然后处理 `struct of_intc_desc *desc`。先设置好 `desc->irq_init_cb` 和 `desc->dev`。然后处理 `desc->interrupt_parent`。先 looks for a property called "interrupts-extended" within the device's node with `of_parse_phandle`。如果失败，return NULL，然后再用 `of_irq_find_parent`。This function walks up the Device Tree, starting from the current device node (np), looking for the nearest ancestor node that has an "interrupt-controller" property。It's possible that the device node np itself has an "interrupt-controller" property, causing `of_irq_find_parent` to return a pointer to np itself. The pointer is then set to NULL to clearly signal that no valid interrupt parent was found.最后把 `desc` 加到 `intc_desc_list`。

然后对 `intc_desc_list` 的每个 entry 进行处理，最重要的一步就是 call `desc->irq_init_cb`。

总结起来，`of_irq_init` call 了 `irq-riscv-intc.c:riscv_intc_init`。

#### 辅助函数 riscv_intc_init

`kernel/irq/handle.c:set_handle_irq` 把 `handle_arch_irq` 函数指针设置为 `riscv_intc_irq`。

```c
// drivers/irqchip/irq-riscv-intc.c

static int __init riscv_intc_init(struct device_node *node,
				  struct device_node *parent)
{
	struct irq_chip *chip = &riscv_intc_chip;
	unsigned long hartid;
	int rc;

	// 找到中断控制器所属 hart
	rc = riscv_of_parent_hartid(node, &hartid);
	if (rc < 0) {
		pr_warn("unable to find hart id for %pOF\n", node);
		return 0;
	}

	/*
	 * The DT will have one INTC DT node under each CPU (or HART)
	 * DT node so riscv_intc_init() function will be called once
	 * for each INTC DT node. We only need to do INTC initialization
	 * for the INTC DT node belonging to boot CPU (or boot HART).
	 */
	// smp_processor_id 返回当前 CPU id，当前 CPU 就是 boot hart
	if (riscv_hartid_to_cpuid(hartid) != smp_processor_id()) {
		/*
		 * The INTC nodes of each CPU are suppliers for downstream
		 * interrupt controllers (such as PLIC, IMSIC and APLIC
		 * direct-mode) so we should mark an INTC node as initialized
		 * if we are not creating IRQ domain for it.
		 */
		fwnode_dev_initialized(of_fwnode_handle(node), true);
		return 0;
	}

	// 处理 andestech
	if (of_device_is_compatible(node, "andestech,cpu-intc")) {
		riscv_intc_custom_base = ANDES_SLI_CAUSE_BASE;
		riscv_intc_custom_nr_irqs = ANDES_RV_IRQ_LAST;
		chip = &andes_intc_chip;
	}

	return riscv_intc_init_common(of_fwnode_handle(node), chip);
}

// drivers/irqchip/irq-riscv-intc.c

static int __init riscv_intc_init_common(struct fwnode_handle *fn, struct irq_chip *chip)
{
	int rc;

	intc_domain = irq_domain_create_tree(fn, &riscv_intc_domain_ops, chip);
	if (!intc_domain) {
		pr_err("unable to add IRQ domain\n");
		return -ENXIO;
	}

	if (riscv_isa_extension_available(NULL, SxAIA)) {
		riscv_intc_nr_irqs = 64;
		rc = set_handle_irq(&riscv_intc_aia_irq);
	} else {
		// 重点
		// This function hooks the interrupt controller's
		// main handler into the low-level CPU trap entry
		// code. When the CPU takes an interrupt,
		// the generic trap handler
		// will call the function registered here.
		rc = set_handle_irq(&riscv_intc_irq);
	}
	if (rc) {
		pr_err("failed to set irq handler\n");
		return rc;
	}

	riscv_set_intc_hwnode_fn(riscv_intc_hwnode);

	pr_info("%d local interrupts mapped%s\n",
		riscv_intc_nr_irqs,
		riscv_isa_extension_available(NULL, SxAIA) ? " using AIA" : "");
	if (riscv_intc_custom_nr_irqs)
		pr_info("%d custom local interrupts mapped\n", riscv_intc_custom_nr_irqs);

	return 0;
}

// drivers/irqchip/irq-riscv-intc.c

static void riscv_intc_irq(struct pt_regs *regs)
{
	unsigned long cause = regs->cause & ~CAUSE_IRQ_FLAG;

	if (generic_handle_domain_irq(intc_domain, cause))
		pr_warn_ratelimited("Failed to handle interrupt (cause: %ld)\n", cause);
}
```

输出：`[    0.000000] riscv-intc: 64 local interrupts mapped`。

### rest_init（SMP）

`init/main.c:rest_init` 创建用户线程 `user_mode_thread(kernel_init, NULL, CLONE_FS);`.

`init/main.c:kernel_init` call `kernel_init_freeable`。

`init/main.c:kernel_init_freeable` call `smp_init`。`smp_init` is called by boot processor to activate the rest.

`kernel/smp.c:smp_init` call `bringup_nonboot_cpus`。

`kernel/cpu.c:bringup_nonboot_cpus` call `cpuhp_bringup_mask`。

`kernel/cpu.c:cpuhp_bringup_mask` call `cpu_up(cpu, CPUHP_ONLINE)`。

`kernel/cpu.c:cup_up` call `_cpu_up(cpu, 0, CPUHP_ONLINE)`。

`kernel/cpu.c:_cpu_up` call `ret = cpuhp_up_callbacks(cpu, st, target);`。

`kernel/cpu.c:cpuhp_up_callbacks` call `cpuhp_invoke_callback_range(true, cpu, st, target);`。

`kernel/cpu.c:cpuhp_invoke_callback_range` call `__cpuhp_invoke_callback_range(bringup, cpu, st, target, false)`。

...

最终 `kernel/cpu.c:bringup_cpu` 会被调用。

`kernel/cpu.c:bringup_cpu` call `__cpu_up`

`arch/riscv/kernel/smpboot.c:__cpu_up` call `start_secondary_cpu`。

```c
// arch/riscv/kernel/smpboot.c

static int start_secondary_cpu(int cpu, struct task_struct *tidle)
{
	if (cpu_ops->cpu_start)
		return cpu_ops->cpu_start(cpu, tidle);

	return -EOPNOTSUPP;
}
```

`cpu_ops` 前面已经设置好了，`cpu_start` 是 `sbi_cpu_start`。call `sbi_cpu_start`。

```c
// arch/riscv/kernel/cpu_ops_sbi.c

static int sbi_cpu_start(unsigned int cpuid, struct task_struct *tidle)
{
	unsigned long boot_addr = __pa_symbol(secondary_start_sbi);
	unsigned long hartid = cpuid_to_hartid_map(cpuid);
	unsigned long hsm_data;
	struct sbi_hart_boot_data *bdata = &per_cpu(boot_data, cpuid);

	/* Make sure tidle is updated */
	smp_mb();
	bdata->task_ptr = tidle;
	bdata->stack_ptr = task_pt_regs(tidle);
	/* Make sure boot data is updated */
	smp_mb();
	hsm_data = __pa(bdata);
	// 启动这个 CPU
	return sbi_hsm_hart_start(hartid, boot_addr, hsm_data);
}
```

## 其他 hart

### secondary_start_sbi

前面 `sbi_cpu_start` 里设置其他 hart 从 `secondary_start_sbi` 开始运行。`secondary_start_sbi` 结构和 `_start_kernel` 类似。

```
// arch/riscv/kernel/head.S

#ifdef CONFIG_SMP
	.global secondary_start_sbi
secondary_start_sbi:
	/* Mask all interrupts */
	csrw CSR_IE, zero
	csrw CSR_IP, zero

#ifndef CONFIG_RISCV_M_MODE
	/* Enable time CSR */
	li t0, 0x2
	csrw CSR_SCOUNTEREN, t0
#endif

	/* Load the global pointer */
	load_global_pointer

	/*
	 * Disable FPU & VECTOR to detect illegal usage of
	 * floating point or vector in kernel space
	 */
	li t0, SR_FS_VS
	csrc CSR_STATUS, t0

	/* Set trap vector to spin forever to help debug */
	la a3, .Lsecondary_park
	csrw CSR_TVEC, a3

	/* a0 contains the hartid & a1 contains boot data */
	li a2, SBI_HART_BOOT_TASK_PTR_OFFSET
	XIP_FIXUP_OFFSET a2
	add a2, a2, a1
	REG_L tp, (a2)
	li a3, SBI_HART_BOOT_STACK_PTR_OFFSET
	XIP_FIXUP_OFFSET a3
	add a3, a3, a1
	REG_L sp, (a3)

.Lsecondary_start_common:

#ifdef CONFIG_MMU
	/* Enable virtual memory and relocate to virtual address */
	la a0, swapper_pg_dir
	XIP_FIXUP_OFFSET a0
	call relocate_enable_mmu
#endif
	call .Lsetup_trap_vector	// 见上，stvec 也被设置为 handle_exception
	scs_load_current		// 见上
	call smp_callin
#endif /* CONFIG_SMP */
```

### smp_callin

```c
// arch/riscv/kernel/smpboot.c

/*
 * C entry point for a secondary processor.
 */
asmlinkage __visible void smp_callin(void)
{
	struct mm_struct *mm = &init_mm;
	unsigned int curr_cpuid = smp_processor_id();

	if (has_vector()) {
		/*
		 * Return as early as possible so the hart with a mismatching
		 * vlen won't boot.
		 */
		if (riscv_v_setup_vsize())
			return;
	}

	/* All kernel threads share the same mm context.  */
	mmgrab(mm);
	current->active_mm = mm;

	store_cpu_topology(curr_cpuid);
	notify_cpu_starting(curr_cpuid);

	riscv_ipi_enable();

	numa_add_cpu(curr_cpuid);

	pr_debug("CPU%u: Booted secondary hartid %lu\n", curr_cpuid,
		cpuid_to_hartid_map(curr_cpuid));

	set_cpu_online(curr_cpuid, true);

	/*
	 * Remote cache and TLB flushes are ignored while the CPU is offline,
	 * so flush them both right now just in case.
	 */
	local_flush_icache_all();
	local_flush_tlb_all();
	// The BSP, which was waiting in __cpu_up,
	// now sees that the core is running.
	complete(&cpu_running);
	/*
	 * Disable preemption before enabling interrupts, so we don't try to
	 * schedule a CPU that hasn't actually started yet.
	 */
	local_irq_enable();
	// marks the CPU as fully online and enters the idle loop.
	// The kernel scheduler is now free to assign tasks to this newly available core.
	cpu_startup_entry(CPUHP_AP_ONLINE_IDLE);
}
```
