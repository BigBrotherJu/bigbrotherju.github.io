# Introduction

> This document mainly contains excerpts from https://www.sco.com/developers/gabi/latest/contents.html and RISC-V ABI.

<c>ELF (Executable and Linking Format) is one format that describes the object file.</c>

## Types of Object File

There are three main types of object files:

- Relocatable file（可重定位文件）

  A **relocatable file** holds code and data suitable for linking with other object files to create an **executable** or a **shared object file**.

- Executable file（可执行文件）

  An **executable file** holds a program suitable for execution; the file specifies how exec(BA_OS) creates a program's process image.

- Shared object file（可共享目标文件）

  A **shared object file** holds code and data suitable for linking in two contexts.

  First, the link editor [see ld(BA_OS)] processes the shared object file with other relocatable and shared object files to create another object file.

  Second, the dynamic linker combines it with an executable file and other shared objects to create a process image.

## Overall Format of Object File

Files used to build a process image (execute a program) must have a program header table; relocatable files do not need one.

Files used during linking must have a section header table; other object files may or may not have one.

```
+----------------------+          +----------------------+
| ELF Header           |          | ELF Header           |
+----------------------+          +----------------------+
| Program header table |          | Program header table |
| optional             |          | required             |
+----------------------+          +----------------------+
| Section 1            |          | Segment 1            |
+----------------------+          +----------------------+
| ...                  |          | Segment 2            |
+----------------------+          +----------------------+
| Section n            |          | Segment 3            |
+----------------------+          +----------------------+
| ...                  |          | ...                  |
+----------------------+          +----------------------+
| Section header table |          | Section header table |
| required             |          | optional             |
+----------------------+          +----------------------+

 Linking View                      Execution View
```

- Order of these structures

  Although the figure shows the program header table immediately after the ELF header, and the section header table following the sections, actual files may differ.

  Moreover, sections and segments have no specified order.

  Only the ELF header has a fixed position in the file.

## Data Representation

- Machine-independent control data

  Object files therefore represent some **control data** with a machine-independent format, making it possible to identify object files and interpret their contents in a common way.

- Remaing data depend on target

  Remaining data in an object file use the encoding of the target processor, regardless of the machine on which the file was created.

32-Bit Data Types：

| Name | Size | Alignment | Purpose |
| :--- | ---  | ---       | :---    |
| `Elf32_Addr`    | 4 | 4 | Unsigned program address |
| `Elf32_Off`     | 4 | 4 | Unsigned file offset     |
| `Elf32_Half`    | 2 | 2 | Unsigned medium integer  |
| `Elf32_Word`    | 4 | 4 | Unsigned integer         |
| `Elf32_Sword`   | 4 | 4 | Signed integer           |
| `unsigned char` | 1 | 1 | Unsigned small integer   |

64-Bit Data Types:

| Name | Size | Alignment | Purpose |
| :--- | ---  | ---       | :---    |
| `Elf64_Addr`    | 8 | 8 | Unsigned program address |
| `Elf64_Off`     | 8 | 8 | Unsigned file offset     |
| `Elf64_Half`    | 2 | 2 | Unsigned medium integer  |
| `Elf64_Word`    | 4 | 4 | Unsigned integer         |
| `Elf64_Sword`   | 4 | 4 | Signed integer           |
| `Elf64_Xword`   | 8 | 8 | Unsigned long integer    |
| `Elf64_Sxword`  | 8 | 8 | Signed long integer      |
| `unsigned char` | 1 | 1 | Unsigned small integer   |

- Alignment

  All data structures that the object file format defines follow the ``natural'' size and alignment guidelines for the relevant *class*.

  If necessary, data structures contain explicit padding to ensure 8-byte alignment for 8-byte *objects*, 4-byte alignment for 4-byte *objects*, to force structure sizes to a multiple of 4 or 8, and so forth.

  Data also have suitable alignment from the beginning of the file.

  Thus, for example, a structure containing an `Elf32_Addr` member will be aligned on a 4-byte boundary within the file.

## Data Structures

```c
typedef struct {
        unsigned char   e_ident[EI_NIDENT]; // 16 bytes
        Elf64_Half      e_type;      // 2 bytes
        Elf64_Half      e_machine;   // 2 bytes
        Elf64_Word      e_version;   // 4 bytes
        Elf64_Addr      e_entry;     // 8 bytes
        Elf64_Off       e_phoff;     // 8 bytes
        Elf64_Off       e_shoff;     // 8 bytes
        Elf64_Word      e_flags;     // 4 bytes
        Elf64_Half      e_ehsize;    // 2 bytes
        Elf64_Half      e_phentsize; // 2 bytes
        Elf64_Half      e_phnum;     // 2 bytes
        Elf64_Half      e_shentsize; // 2 bytes
        Elf64_Half      e_shnum;     // 2 bytes
        Elf64_Half      e_shstrndx;  // 2 bytes
} Elf64_Ehdr; // Elf header: 64 bytes

typedef struct {
	Elf64_Word	sh_name;      // 4 bytes
	Elf64_Word	sh_type;      // 4 bytes
	Elf64_Xword	sh_flags;     // 8 bytes
	Elf64_Addr	sh_addr;      // 8 bytes
	Elf64_Off	sh_offset;    // 8 bytes
	Elf64_Xword	sh_size;      // 8 bytes
	Elf64_Word	sh_link;      // 4 bytes
	Elf64_Word	sh_info;      // 4 bytes
	Elf64_Xword	sh_addralign; // 8 bytes
	Elf64_Xword	sh_entsize;   // 8 bytes
} Elf64_Shdr; // Section header: 64 bytes

typedef struct {
	Elf64_Word	st_name;  // 4 bytes
	unsigned char	st_info;  // 1 byte
	unsigned char	st_other; // 1 byte
	Elf64_Half	st_shndx; // 2 bytes
	Elf64_Addr	st_value; // 8 bytes
	Elf64_Xword	st_size;  // 8 bytes
} Elf64_Sym; // Symbol: 24 bytes
```
