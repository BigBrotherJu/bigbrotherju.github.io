# Misaligned Access in RISC-V

## 如何处理 misaligned access

- Aligned accesses do not raise exception

  Regardless of EEI, loads and stores whose effective addresses are naturally aligned shall not raise an address-misaligned exception.

- Misaligned access behavior depends on EEI

  Loads and stores where the effective address is not naturally aligned to the referenced datatype (i.e., on a four-byte boundary for 32-bit accesses, and a two-byte boundary for 16-bit accesses) have behavior dependent on the EEI.

- EEI provide invisible support: hardware or invisible trap to EEI

  An EEI may guarantee that misaligned loads and stores are fully supported, and so the software running inside the execution environment will never experience a contained or fatal address-misaligned trap.

  In this case, the misaligned loads and stores can be handled in hardware, or via an invisible trap into the execution environment implementation, or possibly a combination of hardware and invisible trap depending on address.

- EEI may not provide invisible support, contained or fatal exceptions may be raised

  An EEI may not guarantee misaligned loads and stores are handled invisibly.

  In this case, loads and stores that are not naturally aligned may either complete execution successfully or raise an exception.

  The exception raised can be either an address-misaligned exception or an access-fault exception. For a memory access that would otherwise be able to complete except for the misalignment, an access exception can be raised instead of an address-misaligned exception if the misaligned access should not be emulated, e.g., if accesses to the memory region have side effects.

  When an EEI does not guarantee misaligned loads and stores are handled invisibly, the EEI must define if exceptions caused by address misalignment result in a contained trap (allowing software running inside the execution environment to handle the trap) or a fatal trap (terminating execution).

- Misaligned access 总结

  Misaligned access 要么硬件直接处理，要么 invisible trap 处理，要么 contained trap 处理，要么 fatal trap。

## Linux config

Misaligned access 硬件处理对应 RISCV_EFFICIENT_UNALIGNED_ACCESS。

invisible trap 处理对应 RISCV_SLOW_UNALIGNED_ACCESS。

contained trap 处理对应 RISCV_EMULATED_UNALIGNED_ACCESS。

现在只考虑 kernel code 中的 misaligned access。

首先如果有硬件支持，根本不会有 exception。

如果没有硬件支持，会产生 misaligned access exception，且这个 exception 不被代理，则由 opensbi 处理，这属于 invisible trap。

如果没有硬件支持，会产生 misaligned access exception，且这个 exception 被代理到内核态，内核自己会处理，这属于 contained trap。

```
config HAVE_EFFICIENT_UNALIGNED_ACCESS
	bool
	help
	  Some architectures are unable to perform unaligned accesses
	  without the use of get_unaligned/put_unaligned. Others are
	  unable to perform such accesses efficiently (e.g. trap on
	  unaligned access and require fixing it up in the exception
	  handler.)

	  This symbol should be selected by an architecture if it can
	  perform unaligned accesses efficiently to allow different
	  code paths to be selected for these cases. Some network
	  drivers, for example, could opt to not fix up alignment
	  problems with received packets if doing so would not help
	  much.

	  See Documentation/core-api/unaligned-memory-access.rst for more
	  information on the topic of unaligned memory accesses.

config RISCV_MISALIGNED
	bool
	help
	  Embed support for detecting and emulating misaligned
	  scalar or vector loads and stores.

config RISCV_SCALAR_MISALIGNED
	bool
	select RISCV_MISALIGNED
	select SYSCTL_ARCH_UNALIGN_ALLOW
	help
	  Embed support for emulating misaligned loads and stores.

config RISCV_VECTOR_MISALIGNED
	bool
	select RISCV_MISALIGNED
	depends on RISCV_ISA_V
	help
	  Enable detecting support for vector misaligned loads and stores.

choice
	prompt "Unaligned Accesses Support"
	default RISCV_PROBE_UNALIGNED_ACCESS
	help
	  This determines the level of support for unaligned accesses. This
	  information is used by the kernel to perform optimizations. It is also
	  exposed to user space via the hwprobe syscall. The hardware will be
	  probed at boot by default.

config RISCV_PROBE_UNALIGNED_ACCESS
	bool "Probe for hardware unaligned access support"
	select RISCV_SCALAR_MISALIGNED
	help
	  During boot, the kernel will run a series of tests to determine the
	  speed of unaligned accesses. This probing will dynamically determine
	  the speed of unaligned accesses on the underlying system. If unaligned
	  memory accesses trap into the kernel as they are not supported by the
	  system, the kernel will emulate the unaligned accesses to preserve the
	  UABI.

config RISCV_EMULATED_UNALIGNED_ACCESS
	bool "Emulate unaligned access where system support is missing"
	select RISCV_SCALAR_MISALIGNED
	help
	  If unaligned memory accesses trap into the kernel as they are not
	  supported by the system, the kernel will emulate the unaligned
	  accesses to preserve the UABI. When the underlying system does support
	  unaligned accesses, the unaligned accesses are assumed to be slow.

config RISCV_SLOW_UNALIGNED_ACCESS
	bool "Assume the system supports slow unaligned memory accesses"
	depends on NONPORTABLE
	help
	  Assume that the system supports slow unaligned memory accesses. The
	  kernel and userspace programs may not be able to run at all on systems
	  that do not support unaligned memory accesses.

config RISCV_EFFICIENT_UNALIGNED_ACCESS
	bool "Assume the system supports fast unaligned memory accesses"
	depends on NONPORTABLE
	select DCACHE_WORD_ACCESS if MMU
	select HAVE_EFFICIENT_UNALIGNED_ACCESS
	help
	  Assume that the system supports fast unaligned memory accesses. When
	  enabled, this option improves the performance of the kernel on such
	  systems. However, the kernel and userspace programs will run much more
	  slowly, or will not be able to run at all, on systems that do not
	  support efficient unaligned memory accesses.

endchoice

choice
	prompt "Vector unaligned Accesses Support"
	depends on RISCV_ISA_V
	default RISCV_PROBE_VECTOR_UNALIGNED_ACCESS
	help
	  This determines the level of support for vector unaligned accesses. This
	  information is used by the kernel to perform optimizations. It is also
	  exposed to user space via the hwprobe syscall. The hardware will be
	  probed at boot by default.

config RISCV_PROBE_VECTOR_UNALIGNED_ACCESS
	bool "Probe speed of vector unaligned accesses"
	select RISCV_VECTOR_MISALIGNED
	depends on RISCV_ISA_V
	help
	  During boot, the kernel will run a series of tests to determine the
	  speed of vector unaligned accesses if they are supported. This probing
	  will dynamically determine the speed of vector unaligned accesses on
	  the underlying system if they are supported.

config RISCV_SLOW_VECTOR_UNALIGNED_ACCESS
	bool "Assume the system supports slow vector unaligned memory accesses"
	depends on NONPORTABLE
	help
	  Assume that the system supports slow vector unaligned memory accesses. The
	  kernel and userspace programs may not be able to run at all on systems
	  that do not support unaligned memory accesses.

config RISCV_EFFICIENT_VECTOR_UNALIGNED_ACCESS
	bool "Assume the system supports fast vector unaligned memory accesses"
	depends on NONPORTABLE
	help
	  Assume that the system supports fast vector unaligned memory accesses. When
	  enabled, this option improves the performance of the kernel on such
	  systems. However, the kernel and userspace programs will run much more
	  slowly, or will not be able to run at all, on systems that do not
	  support efficient unaligned memory accesses.

endchoice
```

## Atomicity

Aligned access 一定是原子的，unaligned access 不一定。

Furthermore, whereas naturally aligned loads and stores are guaranteed to execute atomically, misaligned loads and stores might not, and hence require additional synchronization to ensure atomicity.
