# Sections

- Concepts

  - Section header table (`Elf32_Shdr[]/Elf64_Shdr[]`)
    - Offset from the beginning of file (`e_shoff`)
    - Number of entries (`e_shnum`)
    - Size of each entry (`e_shentsize`)
  - Section header table index
  - Section header (`Elf32_Shdr/Elf64_Shdr`)
    - Setion header that don't have a section
      - Section header at index 0
  - Section
    - String table section
      - Section header string table section
      - String table section for symbol table
    - Other special sections

- Relations

  - `Elf64_Shdr_array[0]->sh_size <-> Elf64_Ehdr->e_shnum`

  - `Elf64_Shdr_array[0]->sh_link <-> Elf64_Ehdr->e_shstrndx`

  - `SHT_SYMTAB_SHNDX` type section <-> `SHT_SYMTAB` type section

  - `SHF_INFO_LINK` flagged section <-> this section header's `sh_info`

  - Section and section header

    Every section in an object file has exactly one section header describing it.

    Section headers may exist that do not have a section.

  - Section and section group

    A section cannot be a member of more than one group.

  - Section and section name

    An object file may have more than one section with the same name.

## Section Header Table and Table Index

The section header table is an array of `Elf32_Shdr` or `Elf64_Shdr` structures as described below.

A section header table index is a subscript into this array.

Special section header table indexes:

```
Name           Value   Meaning
SHN_UNDEF [1]  0       This value marks an undefined, missing, irrelevant, or
                       otherwise meaningless section reference.
                       For example, a symbol ``defined'' relative to section
                       number SHN_UNDEF is an undefined symbol.

SHN_LORESERVE  0xff00  Lower bound of the range of reserved indexes.

SHN_LOPROC [2] 0xff00  Values in this inclusive range are reserved for
SHN_HIPROC     0xff1f  processor-specific semantics.

SHN_LOOS       0xff20  Values in this inclusive range are reserved for
SHN_HIOS       0xff3f  OS-specific semantics.

SHN_ABS        0xfff1  This value specifies absolute values for the
                       corresponding reference.
                       For example, symbols defined relative to section number
                       SHN_ABS have absolute values and are not affected by
                       relocation.

SHN_COMMON     0xfff2  Symbols defined relative to this section are common
                       symbols, such as unallocated C external variables.

SHN_XINDEX     0xffff  This value is an escape value. It indicates that the
                       actual section header index is too large to fit in the
                       containing field and is to be found in another location

SHN_HIRESERVE  0xffff  Upper bound of the range of reserved indexes
[3]
```

01. Section header table contains an entry for 0

    Although index 0 is reserved as the undefined value, the section header table contains an entry for index 0.

02. RISC-V ABI does not define values in this range.

03. Section header table does not contain entries for reserved indexes

    The system reserves indexes between `SHN_LORESERVE` and `SHN_HIRESERVE`, inclusive; the values do not reference the section header table.

    The section header table does not contain entries for the reserved indexes.

## Section Header

```c
typedef struct {
	Elf32_Word	sh_name;      // 4 bytes
	Elf32_Word	sh_type;      // 4 bytes
	Elf32_Word	sh_flags;     // 4 bytes
	Elf32_Addr	sh_addr;      // 4 bytes
	Elf32_Off	sh_offset;    // 4 bytes
	Elf32_Word	sh_size;      // 4 bytes
	Elf32_Word	sh_link;      // 4 bytes
	Elf32_Word	sh_info;      // 4 bytes
	Elf32_Word	sh_addralign; // 4 bytes
	Elf32_Word	sh_entsize;   // 4 bytes
} Elf32_Shdr; // 40 bytes

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
} Elf64_Shdr; // 64 bytes
```

```
Member   Purpose
         Possible Value

sh_name  Specifies name of the section
         Index into the section header string table section

sh_type ========================================================================
SHT_NULL          0  This value marks the section header as inactive; it does
                     not have an associated section. Other members of the
                     section header have undefined values.

SHT_PROGBITS      1  The section holds information defined by the program, whose
                     format and meaning are determined solely by the program.

SHT_SYMTAB [1]    2  SHT_SYMTAB provides symbols for link editing, though it may
SHT_DYNSYM        11 also be used for dynamic linking. As a complete symbol
                     table, it may contain many symbols unnecessary for dynamic
                     linking.
                     Consequently, an object file may also contain a SHT_DYNSYM
                     section, which holds a minimal set of dynamic linking
                     symbols, to save space

SHT_STRTAB [2]    3  The section holds a string table.

SHT_RELA [2]      4  The section holds relocation entries with explicit addends
SHT_REL  [2]      9  The section holds relocation entries w/o explicit addends

SHT_HASH [1]      5  The section holds a symbol hash table.
SHT_DYNAMIC [1]   6  The section holds information for dynamic linking.
SHT_NOTE          7  The section holds information that marks the file in some
                     way

SHT_NOBITS        8  A section of this type occupies no space in the file but
                     otherwise resembles SHT_PROGBITS.
                     SHT_NOBITS section occupies no space in the file, but its
                     sh_offset member contains the conceptual file offset.
                     SHT_NOBITS section occupies no space in the file, but it
                     may have a non-zero sh_size

SHT_SHLIB         10 This section type is reserved but has unspecified semantics

SHT_INIT_ARRAY    14 This section contains an array of pointers to initializa-
                     tion functions
SHT_FINI_ARRAY    15 This section contains an array of pointers to termination
                     functions
SHT_PREINIT_ARRAY 16 This section contains an array of pointers to functions
                     that are invoked before all other initialization functions

SHT_GROUP         17 This section defines a section group.

SHT_SYMTAB_SHNDX  18 This section is associated with a symbol table section and
[6]                  is required if any of the section header indexes referenced
                     by that symbol table contain the escape value SHN_XINDEX.

SHT_LOOS    0x60000000 Values in this inclusive range are reserved for
SHT_HIOS    0x6fffffff OS-specific semantics.

SHT_LOPROC  0x70000000 Values in this inclusive range are reserved for
SHT_HIPROC  0x7fffffff processor-specific semantics. [7]

SHT_LOUSER  0x80000000 Lower bound and upper bound of the range of indexes
SHT_HIUSER  0xffffffff reserved for application programs

sh_flags =======================================================================
SHF_WRITE       0x1   The section contains data that should be writable during
                      process execution.

SHF_ALLOC       0x2   The section occupies memory during process execution.
                      Some control sections do not reside in the memory image of
                      an object file; this attribute is off for those sections.

SHF_EXECINSTR   0x4   The section contains executable machine instructions.

SHF_MERGE [8]   0x10  The data in the section may be merged to eliminate
                      duplication

SHF_STRINGS     0x20  Data elements in the section consist of null-terminated
                      character strings.
                      The size of each character is specified in the section
                      header's sh_entsize field.

SHF_INFO_LINK   0x40  The sh_info field of this section header holds a section
                      header table index.

SHF_LINK_ORDER  0x80  This flag adds special ordering requirements for link
[9]                   editors

SHF_OS_NONCONFORMING  0x100  This section requires special OS-specific
                             processing (beyond the standard linking rules) to
                             avoid incorrect behavior.

SHF_GROUP [10]  0x200 This section is a member (perhaps the only one) of a
                      section group.
                      The section must be referenced by a section of type
                      SHT_GROUP.

SHF_TLS         0x400 This section holds Thread-Local Storage, meaning that
                      each separate execution flow has its own distinct
                      instance of this data.
                      Implementations need not support this flag.

SHF_COMPRESSED  0x800 This flag identifies a section containing compressed data.
[11]

SHF_MASKOS      0x0ff00000  All bits included in this mask are reserved for
                            operating system-specific semantics.
SHF_MASKPROC    0xf0000000  All bits included in this mask are reserved for
                            processor-specific semantics.
================================================================================
sh_addr       If the section will appear in the memory image of a process, this
              member gives the address at which the section's first byte should
              reside. Otherwise, the member contains 0.

sh_offset     This member's value gives the byte offset from the beginning of
              the file to the first byte in the section.

sh_size       This member gives the section's size in bytes.

sh_link       This member holds a section header table index link, whose
              interpretation depends on the section type.

sh_info       This member holds extra information, whose interpretation depends
              on the section type.
              If the sh_flags field for this section header includes the
              attribute SHF_INFO_LINK, then this member represents a section
              header table index.

sh_addralign  The value of sh_addr must be congruent to 0, modulo the value of
              sh_addralign.
              Currently, only 0 and positive integral powers of two are allowed.
              Values 0 and 1 mean the section has no alignment constraints.

sh_entsize    Some sections hold a table of fixed-size entries, such as a
              symbol table. For such a section, this member gives the size in
              bytes of each entry.
              The member contains 0 if the section does not hold a table of
              fixed-size entries.
```

`sh_type` `sh_link` `sh_info` combination:

```
sh_type      sh_link                        sh_info
SHT_DYNAMIC  The section header index of    0
             the *string table* used by
             entries in the section.

SHT_HASH     The section header index of    0
             the *symbol table* to which
             the hash table applies.

SHT_REL      The section header index of    The section header index of the
SHT_RELA     the associated *symbol table*  section to which the relocation
                                            applies.

SHT_SYMTAB   The section header index of    One greater than the symbol table
SHT_DYNSYM   the associated *string table*  index of the last local symbol
                                            (binding STB_LOCAL).

SHT_GROUP    The section header index of    The symbol table index of an entry
             the associated *symbol table*  in the associated symbol table.
                                            The name of the specified symbol
                                            table entry provides a signature
                                            for the section group.

SHT_SYMTAB_SHNDX  The section header index of    0
                  the associated *symbol table*
                  section.
```

01. Currently, an object file may have only one section of this type, but this restriction may be relaxed in the future.

02. An object file may have multiple sections of this type.

06. `SHT_SYMTAB_SHNDX`

    `SHT_SYMTAB_SHNDX` section 里的值要么是 0，要么是对应的 symbol table entry 的 section header index。

    The section is an array of `Elf32_Word` values.

    Each value corresponds **one to one** with a symbol table entry and appear in the same order as those entries.

    The values represent the section header indexes against which the symbol table entries are defined.

    Only if the corresponding symbol table entry's `st_shndx` field contains the escape value `SHN_XINDEX` will the matching `Elf32_Word` hold the actual section header index;

    otherwise, the entry must be `SHN_UNDEF` (0).

07. RISC-V ABI does not define values in this range.

08. `SHF_MERGE`

    Each element in the section is compared against other elements in sections with the **same name, type and flags**.

    Elements that would have identical values at program run-time may be merged.

    Relocations referencing elements of such sections must be resolved to the merged locations of the referenced values.

    Note that any relocatable values, including values that would result in run-time relocations, must be analyzed to determine whether the run-time values would actually be identical.

    An ABI-conforming object file may not depend on specific elements being merged, and an ABI-conforming link editor may choose not to merge specific elements.

09. `SHF_LINK_ORDER`

    A typical use of this flag is to build a table that references text or data sections in address order.

10. `SHF_GROUP`

    The `SHF_GROUP` flag may be set only for sections contained in **relocatable objects** (objects with the ELF header `e_type` member set to `ET_REL`).

11. `SHF_COMPRESSED`

    `SHF_COMPRESSED` applies only to non-allocable sections, and cannot be used in conjunction with `SHF_ALLOC`.

    In addition, `SHF_COMPRESSED` cannot be applied to sections of type `SHT_NOBITS`.

### Section Header at Index 0

Although index 0 is reserved as the undefined value, the section header table contains an entry for index 0.

Section header table entry at index 0:

```
Name      Value        Note
sh_name   0            No name
sh_type   SHT_NULL     Inactive
sh_flags  0            No flags
sh_addr   0            No address
sh_offset 0            No offset
sh_size   Unspecified  If non-zero, the actual number of section header entries
sh_link   Unspecified  If non-zero, the index of the section header string
                       table section
sh_info       0        No auxiliary information
sh_addralign  0        No alignment
sh_entsize    0        No entries
```

> [!NOTE]
> If `e_shnum` and `e_shstrndx` are greater than or equal to `SHN_LORESERVE` (`0xff00`), the actual values are contained in the `sh_size` and `sh_link` field of the section header at index 0.

## Sections

### Compressed Sections

Compressed sections begin with a compression header structure that identifies the compression algorithm.

``` c
typedef struct {
	Elf32_Word	ch_type;  // the compression algorithm
	Elf32_Word	ch_size;  // the size in bytes of the uncompressed data
        // the required alignment for the uncompressed data
	Elf32_Word	ch_addralign;
} Elf32_Chdr;

typedef struct {
	Elf64_Word	ch_type;
	Elf64_Word	ch_reserved;
	Elf64_Xword	ch_size;
	Elf64_Xword	ch_addralign;
} Elf64_Chdr;
```

- Relocation

  All relocations to a compressed section specifiy offsets to the uncompressed section data.

  It is therefore necessary to decompress the section data before relocations can be applied.

- Compression algorithms

  Each compressed section specifies the algorithm independently.

  It is permissible for different sections in a given ELF object to employ different compression algorithms.

  ```
  Name                Value
  ELFCOMPRESS_ZLIB    1           The section data is compressed with the ZLIB
                                  algoritm.
  ELFCOMPRESS_LOOS    0x60000000  OS-specific semantics
  ELFCOMPRESS_HIOS    0x6fffffff
  ELFCOMPRESS_LOPROC  0x70000000  processor-specific semantics
  ELFCOMPRESS_HIPROC  0x7fffffff
  ```

### Special Sections

See [System V gABI](https://www.sco.com/developers/gabi/latest/ch4.sheader.html#special_sections) for detailed explanation.

```
Name            Type               Attributes
.bss            SHT_NOBITS         SHF_ALLOC+SHF_WRITE
.comment        SHT_PROGBITS       none
.data           SHT_PROGBITS       SHF_ALLOC+SHF_WRITE
.data1          SHT_PROGBITS       SHF_ALLOC+SHF_WRITE
.debug          SHT_PROGBITS       none
.dynamic        SHT_DYNAMIC        SHF_ALLOC[+SHF_WRITE]
.dynstr         SHT_STRTAB         SHF_ALLOC
.dynsym         SHT_DYNSYM         SHF_ALLOC
.fini           SHT_PROGBITS       SHF_ALLOC+SHF_EXECINSTR
.fini_array     SHT_FINI_ARRAY     SHF_ALLOC+SHF_WRITE
.got            SHT_PROGBITS       see below
.hash           SHT_HASH           SHF_ALLOC
.init           SHT_PROGBITS       SHF_ALLOC+SHF_EXECINSTR
.init_array     SHT_INIT_ARRAY     SHF_ALLOC+SHF_WRITE
.interp         SHT_PROGBITS       see below
.line           SHT_PROGBITS       none
.note           SHT_NOTE           none
.plt            SHT_PROGBITS       see below
.preinit_array  SHT_PREINIT_ARRAY  SHF_ALLOC+SHF_WRITE
.relname        SHT_REL            see below
.relaname       SHT_RELA           see below
.rodata         SHT_PROGBITS       SHF_ALLOC
.rodata1        SHT_PROGBITS       SHF_ALLOC
.shstrtab       SHT_STRTAB         none
.strtab         SHT_STRTAB         see below
.symtab         SHT_SYMTAB         see below
.symtab_shndx   SHT_SYMTAB_SHNDX   see below
.tbss           SHT_NOBITS         SHF_ALLOC+SHF_WRITE+SHF_TLS
.tdata          SHT_PROGBITS       SHF_ALLOC+SHF_WRITE+SHF_TLS
.tdata1         SHT_PROGBITS       SHF_ALLOC+SHF_WRITE+SHF_TLS
.text           SHT_PROGBITS       SHF_ALLOC+SHF_EXECINSTR
```

## Section Group

A section group is a set of sections that are related and that must be treated specially by the linker.

- `SHT_GROUP` defines a section group

  Sections of type `SHT_GROUP` may appear only in relocatable objects

- `SHF_GROUP` is a member (perhaps the only one) of a section group

  `SHF_GROUP` section must be referenced by a section of type `SHT_GROUP`.

  The `SHF_GROUP` flag may be set only for sections contained in relocatable objects

- Section header table entry: group before member

  The section header table entry for a group section must appear in the section header table before the entries for any of the sections that are members of the group.

- Signature and header of the section group

  The name of a symbol from one of the containing object's symbol tables provides a signature for the section group.

  The section header of the `SHT_GROUP` section specifies the identifying symbol entry, as described above:

  - the `sh_link` member contains the section header index of the symbol table section that contains the entry.
  - The `sh_info` member contains the symbol table index of the identifying entry.
  - The `sh_flags` member of the section header contains 0.
  - The name of the section (`sh_name`) is not specified.

  The referenced signature symbol is not restricted. Its containing symbol table section need not be a member of the group, for example.

- Content of section group

  The section data of a `SHT_GROUP` section is an array of `Elf32_Word` entries.

  The first entry is a flag word. The remaining entries are a sequence of section header indices.

  The following flags are currently defined:

  ```
  GRP_COMDAT    0x1
  GRP_MASKOS    0x0ff00000
  GRP_MASKPROC  0xf0000000
  ```

  The section header indices in the `SHT_GROUP` section identify the sections that make up the group.

  Each such section must have the `SHF_GROUP` flag set in its `sh_flags` section header member.

## String Table Section

String table sections hold null-terminated character sequences, commonly called strings.

- Symbol and section name

  The object file uses these strings to represent symbol and section names.

- How to reference a string

  One references a string as an index into the string table section.

- First byte and last byte is 0

  The first byte, which is index zero, is defined to hold a null character.

  Likewise, a string table's last byte is defined to hold a null character, ensuring null termination for all strings.

- String whose index is 0

  A string whose index is zero specifies either no name or a null name, depending on the context.

- Empty string table section is permitted

  An empty string table section is permitted;

  its section header's `sh_size` member would contain zero.

  Non-zero indexes are invalid for an empty string table.

- Section header string table section

  A section header's `sh_name` member holds an index into the section header string table section, as designated by the `e_shstrndx` member of the ELF header.

