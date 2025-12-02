# ELF Header

```c
#define EI_NIDENT 16

typedef struct {
        unsigned char   e_ident[EI_NIDENT]; // 16 bytes
        Elf32_Half      e_type;       // 2 bytes
        Elf32_Half      e_machine;    // 2 bytes
        Elf32_Word      e_version;    // 4 bytes
        Elf32_Addr      e_entry;      // 4 bytes
        Elf32_Off       e_phoff;      // 4 bytes
        Elf32_Off       e_shoff;      // 4 bytes
        Elf32_Word      e_flags;      // 4 bytes
        Elf32_Half      e_ehsize;     // 2 bytes
        Elf32_Half      e_phentsize;  // 2 bytes
        Elf32_Half      e_phnum;      // 2 bytes
        Elf32_Half      e_shentsize;  // 2 bytes
        Elf32_Half      e_shnum;      // 2 bytes
        Elf32_Half      e_shstrndx;   // 2 bytes
} Elf32_Ehdr; // 52 bytes

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
} Elf64_Ehdr; // 64 bytes
```

## ELF Identification / e_ident

The initial bytes mark the file as an object file and provide machine-independent data with which to decode and interpret the file's contents.

`e_ident[]` indexes and possible values:

```
Name           Value  Purpose              Possible e_ident[EI_*] value
EI_MAG0        0      File identification  ELFMAG0 / 0x7f
EI_MAG1        1      File identification  ELFMAG1 / 'E'
EI_MAG2        2      File identification  ELFMAG1 / 'L'
EI_MAG3        3      File identification  ELFMAG3 / 'F'
--------------------------------------------------------------------------------
EI_CLASS       4      File class [1]       ELFCLASSNONE / 0 / Invalid class
                                           ELFCLASS32   / 1 / 32-bit objects
                                           ELFCLASS64   / 2 / 64-bit objects

EI_DATA        5      Data encoding [2]    ELFDATANONE  / 0 / Invalid data
                                                              encoding
                                           ELFDATA2LSB  / 1 / Little endian
                                           ELFDATA2MSB  / 2 / Big endian

EI_VERSION     6      ELF header version   EV_CURRENT [3]

EI_OSABI       7      OS/ABI-specific ELF  ELFOSABI_NONE / 0 / No extensions or
                      extension identifi-                      unspecified
                      cation [4]           ELFOSABI_HPUX / 1 / Hewlett-Packard
                                                               HP-UX
                                           ...
                                           / 64 - 255 / Architecture-specific
                                                        value range
--------------------------------------------------------------------------------
EI_ABIVERSION  8      ABI version [5]
EI_PAD         9      Start index of pad-  0
                      ding bytes
               10-15  Indexes of padding   0
                      bytes
EI_NIDENT      16     Size of e_ident[]
```

### 1 File Class

- Class defines types used by container data structures

  The class of the file defines the basic types used by the data structures of the object file *container* itself.

- Other data may use different types

  The data contained in object file sections may follow a different programming model. If so, the processor supplement describes the model used.

- 32-bit and 64-bit classes

  Class `ELFCLASS32` supports machines with 32-bit architectures. It uses the basic types defined in the table labeled ``32-Bit Data Types.''

  Class `ELFCLASS64` supports machines with 64-bit architectures. It uses the basic types defined in the table labeled ``64-Bit Data Types.''

### 2 Data Encoding

- Data encoding specifies both container and data

  Byte `e_ident[EI_DATA]` specifies the encoding of both the data structures used by object file container and data contained in object file sections.

<q>Primarily for the convenience of code that looks at the ELF file at runtime, the ELF data structures are intended to have the same **byte order** as that of the running program.</q>

### 3 EV_CURRENT

Currently, `e_ident[EI_VERSION]` must be `EV_CURRENT`, as explained below for `e_version`.

### 4 OS/ABI-specific ELF Extension

Some fields in other ELF structures have flags and values that have operating system and/or ABI specific meanings; the interpretation of those fields is determined by the value of this byte.

- If object file does not use extensions

  If the object file does not use any *extensions*, it is recommended that this byte be set to 0.

- If psABI defines values in 64-255, these values can be used

  If the value for this byte is 64 through 255, its meaning depends on the value of the `e_machine` header member.

  The ABI processor supplement for an architecture can define its own associated set of values for this byte in this range.

- If not, 0-18 shall be used

  If the processor supplement does not specify a set of values, one of the following values shall be used, where 0 can also be taken to mean unspecified.

  > [!NOTE]
  > RISC-V ABI does not define values in this range.

### 5 ABI Version

This field is used to distinguish among incompatible versions of an ABI.

The interpretation of this version number is dependent on the ABI identified by the `EI_OSABI` field.

If no values are specified for the `EI_OSABI` field by the processor supplement or
no version values are specified for the ABI determined by a particular value of the `EI_OSABI` byte,
the value 0 shall be used for the `EI_ABIVERSION` byte; it indicates unspecified.

## Other Members

```
Name         Size   Purpose           Possible value
e_type [1]   2 B    Object file type  ET_NONE   / 0 / No file type
                                      ET_REL    / 1 / Relocatable file
                                      ET_EXEC   / 2 / Executable file
                                      ET_DYN    / 3 / Shared object file
                                      ET_CORE   / 4 / Core file

                                      ET_LOOS   / 0xfe00 / OS-specific
                                      ET_HIOS   / 0xfeff / OS-specific
                                      ET_LOPROC / 0xff00 / Processor-specific
                                      ET_HIPROC / 0xffff / Processor-specific

e_machine    2 B    Specifies archi-  EM_NONE    / 0   / No machine
                    tecture           EM_386     / 3   / Intel 80386
                                      EM_ARM     / 40  / ARM 32-bit architecture
                                                         (AARCH32)
                                      EM_X86_64  / 62  / AMD x86-64 architecture
                                      EM_AARCH64 / 183 / ARM 64-bit architecture
                                                         (AARCH64)
                                      EM_CUDA    / 190 / NV CUDA architecture
                                      EM_AMDGPU  / 224 / AMD GPU architecture
                                      EM_RISCV   / 243 / RISC-V

e_version    4 B    Object file version  EV_NONE    / 0 / Invalid version
[2]                                      EV_CURRENT / 1 / Current version

e_entry      4/8 B  Gives the virtual address to which the system first
                    transfers control, thus starting the process.
                    If the file has no associated entry point, this member holds
                    zero.

e_phoff      4/8 B  The program header table's file offset in bytes.
                    If the file has no program header table, this member holds
                    zero.

e_shoff      4/8 B  The section header table's file offset in bytes.
                    If the file has no section header table, this member holds
                    zero.

e_flags [5]  4 B    Processor-specific flags associated with the file.
                    Flag names take the form EF_machine_flag.

e_ehsize     2 B    ELF header's size in bytes  52 / 64 B

e_phentsize  2 B    The size in bytes of one entry in program header table
                    If a file has no program header table, it holds the value
                    zero.

e_phnum      2 B    The number of entries in the program header table
                    If a file has no program header table, e_phnum holds the
                    value zero.

e_shentsize  2 B    Similar to e_phentsize      40 / 64 B

e_shnum [3]  2 B    Similar to e_phnum

e_shstrndx   2 B    The section header table index of the entry associated with
[4]                 the section name string table.
                    If the file has no section name string table, this member
                    holds the value SHN_UNDEF.
```

### 1 `e_type`

- Core file format is unspecified

  Although the core file contents are **unspecified**, type `ET_CORE` is reserved to mark the file.

  `ET_CORE` 表示的 core file 就是 coredump 里的 core。

- RISC-V does not define values in `[ET_LOPROC, ET_HIPROC]`

  Values from `ET_LOPROC` through `ET_HIPROC` (inclusive) are reserved for processor-specific semantics. If meanings are specified, the processor supplement explains them.

  > [!NOTE]
  > RISC-V ABI does not define values in this range.

### 2 `e_version`

The value 1 signifies the original file format; *extensions* will create new versions with higher numbers.

Although the value of `EV_CURRENT` is shown as 1 in the previous table, it will change as necessary to reflect the current version number.

### 3 `e_shnum`

- Connection between `e_shnum` and 0th section header's `sh_size`

  If the number of sections is greater than or equal to `SHN_LORESERVE` (`0xff00`), this member has the value zero and the actual number of section header table entries is contained in the `sh_size` field of the section header at index 0. (Otherwise, the `sh_size` member of the initial entry contains 0.)

### 4 `e_shstrndx`

- Connection between `e_shstrndx` and 0th section header's `sh_link`

  If the section name string table section index is greater than or equal to `SHN_LORESERVE` (`0xff00`), this member has the value `SHN_XINDEX` (`0xffff`) and the actual index of the section name string table section is contained in the `sh_link` field of the section header at index 0. (Otherwise, the `sh_link` member of the initial entry contains 0.)

### 5 `e_flags` for RISC-V

- These flags are used by linker

  These flags are used by the **linker** to disallow linking ELF files with incompatible ABIs together.

- Layout of `e_flags`

  Table 7 shows the layout of e_flags, and flag details are listed below.

  | Bits 31-24 | Bits 23-5 | Bit 4 | Bit 3 | Bit 2-1 | Bit 0 |
  | --- | --- | --- | --- | --- | --- |
  | Non-standard extensions | Reserved | TSO | RVE | Float ABI | RVC |

- Flag details

  ```
  EF_RISCV_RVC              0x0001
  When linking objects which specify EF_RISCV_RVC, the linker is permitted to
  use RVC instructions such as C.JAL in the linker relaxation process.

  EF_RISCV_FLOAT_ABI_SOFT   0x0000
  EF_RISCV_FLOAT_ABI_SINGLE 0x0002
  EF_RISCV_FLOAT_ABI_DOUBLE 0x0004
  EF_RISCV_FLOAT_ABI_QUAD   0x0006
  EF_RISCV_FLOAT_ABI        0x0006
  This macro is used as a mask to test for one of the above floating-point
  ABIs, e.g., (e_flags & EF_RISCV_FLOAT_ABI) == EF_RISCV_FLOAT_ABI_DOUBLE.

  EF_RISCV_RVE              0x0008
  EF_RISCV_TSO              0x0010
  ```
