# Linux Scheduling Notes

## task_struct

In the Linux kernel, everything that can be scheduled and run on a CPU is considered a task, and each task is represented by a C structure called `task_struct`.

This single data structure is used to represent:

- Traditional heavyweight user processes.
- Lightweight threads created within a process (pthread in user space).
- Kernel threads that run only in kernel mode (e.g., `kswapd`).

## User Program

### Ways to Enter Kernel

A user program can enter the kernel in three main ways:

- by making a system call,
- experiencing a hardware interrupt,
- or causing an exception.

### Forms in Kernel

When you run a user program, the kernel creates a `task_struct` for it.

This single `task_struct` represents your program for its entire lifecycle.

When your user program makes a system call (e.g., to read a file), a hardware interrupt occurs, or an exception happens, the following occurs:

- The CPU switches from user mode to the privileged kernel mode.
- Control is transferred to a specific handler function inside the kernel.

Crucially, this kernel code executes **in the context of the original user process**. It's still the same `task_struct`, and the kernel can access that task's information (like the arguments passed to the system call).

After the kernel finishes its work, it switches the CPU back to user mode and returns control to the user program, right where it left off.

### Kernel Stack

When the kernel creates a `task_struct` to represent a new thread or process, it also allocates a small, fixed-size block of memory to serve as that task's kernel stack.

When a task running in user mode enters the kernel for any reason—a system call, a hardware interrupt, or a page fault—the CPU must immediately switch from using the user stack to this dedicated kernel stack.

## Kernel Thread

A kernel thread is a distinct type of task that runs only in kernel mode and has no user-space address space.

These threads are created by the kernel itself to perform background tasks, like managing memory (`kswapd`) or handling deferred work (`kworker`).

## Possible Scenarios for Running in Kernel

- Initialization process
- User enters kernel because of exceptions (syscall) or interrupt
- Kernel thread
- Kernel enters kernel because of exceptions or interrupt
