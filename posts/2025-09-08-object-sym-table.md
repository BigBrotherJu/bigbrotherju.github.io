# Symbol Table

## Symbol Table Entry

```c
typedef struct {
	Elf32_Word	st_name;  // 4 bytes
	Elf32_Addr	st_value; // 4 bytes
	Elf32_Word	st_size;  // 4 bytes
	unsigned char	st_info;  // 1 byte
	unsigned char	st_other; // 1 byte
	Elf32_Half	st_shndx; // 2 bytes
} Elf32_Sym; // 16 bytes

typedef struct {
	Elf64_Word	st_name;  // 4 bytes
	unsigned char	st_info;  // 1 byte
	unsigned char	st_other; // 1 byte
	Elf64_Half	st_shndx; // 2 bytes
	Elf64_Addr	st_value; // 8 bytes
	Elf64_Xword	st_size;  // 8 bytes
} Elf64_Sym; // 24 bytes
```

```
Name      Purpose

st_name   This member holds an index into the object file's symbol string table
          If the value is non-zero, it represents a string table index that
          gives the symbol name.
          Otherwise, the symbol table entry has no name.

st_value  This member gives the value of the associated symbol.
          Depending on the context, this may be an absolute value, an address,
          and so on;

st_size   Many symbols have associated sizes.
          For example, a data object's size is the number of bytes contained in
          the object.
          This member holds 0 if the symbol has no size or an unknown size.

st_info   This member specifies the symbol's type and binding attributes.
          Least significant 4 bits are type, remaining bits are binding

- binding [1] A symbol's binding determines the linkage visibility and behavior.

  STB_LOCAL   0  Local symbols are not visible outside the object file
                 containing their definition.
                 Local symbols of the same name may exist in multiple files
                 without interfering with each other.

  STB_GLOBAL  1  Global symbols are visible to all object files being combined.
  [2]            One file's definition of a global symbol will satisfy another
                 file's undefined reference to the same global symbol.

  STB_WEAK    2  Weak symbols resemble global symbols, but their definitions
  [2]            have lower precedence.

  STB_LOOS    10 operating system-specific semantics.
  STB_HIOS    12

  STB_LOPROC  13 processor-specific semantics
  STB_HIPROC  15

- type        provides a general classification for the associated entity.

  STT_NOTYPE  0  The symbol's type is not specified.

  STT_OBJECT  1  The symbol is associated with a data object, such as a
                 variable, an array, and so on.

  STT_FUNC    2  The symbol is associated with a function or other executable
  [3]            code.

  STT_SECTION 3  The symbol is associated with a section.
                 Symbol table entries of this type exist primarily for
                 relocation and normally have STB_LOCAL binding.

  STT_FILE    4  Conventionally, the symbol's name gives the name of the source
                 file associated with the object file.
                 A file symbol has STB_LOCAL binding, its section index is
                 SHN_ABS, and it precedes the other STB_LOCAL symbols for the
                 file, if it is present.

  STT_COMMON  5  The symbol labels an uninitialized common block.
  [4]

  STT_TLS     6  The symbol specifies a Thread-Local Storage entity.

  STT_LOOS    10 operating system-specific semantics.
  STT_HIOS    12

  STT_LOPROC  13 processor-specific semantics
  STT_HIPROC  15

st_other  This member currently specifies a symbol's visibility.
          Only lower 2 bits are used, other bits contain 0 and have no defined
          meaning.

- visibility    A symbol's visibility, although it may be specified in a
                relocatable object, defines how that symbol may be accessed once
                it has become part of an executable or shared object.

  STV_DEFAULT   0
  STV_INTERNAL  1
  STV_HIDDEN    2
  STV_PROTECTED 3

st_shndx  Every symbol table entry is defined in relation to some section.
          This member holds the relevant section header table index.
```

01. Precedence

    In each symbol table, all symbols with `STB_LOCAL` binding precede the weak and global symbols.

02. Global and weak symbols differ in two major ways

    First:

    When the link editor combines several relocatable object files, it does not allow multiple definitions of `STB_GLOBAL` symbols with the same name.

    On the other hand, if a defined **global** symbol exists, the appearance of a weak symbol with the same name will not cause an error. The link editor honors the global definition and ignores the weak ones.

    Similarly, if a **common** symbol exists (that is, a symbol whose `st_shndx` field holds `SHN_COMMON`), the appearance of a weak symbol with the same name will not cause an error. The link editor honors the common definition and ignores the weak ones.

    Second:

    When the link editor searches archive libraries [see ``Archive File'' in Chapter 7], it extracts archive members that contain definitions of **undefined global symbols**. The member's definition may be either a global or a weak symbol.

    The link editor does not extract archive members to resolve **undefined weak symbols**. Unresolved weak symbols have a zero value.

03. Function symbols in shared object

    Function symbols (those with type `STT_FUNC`) in shared object files have special significance.

    When another object file references a function from a shared object, the link editor automatically **creates a procedure linkage table entry** for the referenced symbol.

    Shared object symbols with types other than `STT_FUNC` will not be referenced automatically through the procedure linkage table.

04. `STT_COMMON` symbol

    Symbols with type `STT_COMMON` label uninitialized common blocks.

    In relocatable objects, these symbols are not allocated and must have the special section index `SHN_COMMON` (see below).

    In shared objects and executables these symbols must be allocated to some section in the defining object.

    In relocatable objects, symbols with type `STT_COMMON` are treated just as other symbols with index `SHN_COMMON`. If the link-editor allocates space for the `SHN_COMMON` symbol in an output section of the object it is producing, it must preserve the type of the output symbol as `STT_COMMON`.

    When the dynamic linker encounters a reference to a symbol that resolves to a definition of type `STT_COMMON`, it may (but is not required to) change its symbol resolution rules as follows: instead of binding the reference to the first symbol found with the given name, the dynamic linker searches for the first symbol with that name with type other than `STT_COMMON`. If no such symbol is found, it looks for the `STT_COMMON` definition of that name that has the largest size.

## Symbol Visibility

- Visible to other object files

  If a symbol is visible outside the object file containing its definition,

  this symbol can be referenced by other object files during the linking process.

- Hidden

  A symbol defined in the current component is hidden if its name is not visible to other components.

- Preemptable

  Preemptable names may by preempted by definitions of the same name in another component.

- Protected

  A symbol defined in the current component is protected if it is visible in other components but not preemptable

- `STV_DEFAULT`

  The visibility of symbols with the `STV_DEFAULT` attribute is as specified by the symbol's binding type.

  - Global and weak symbols are visible

    That is, global and weak symbols are visible outside of their defining component (executable file or shared object).

  - Local symbols are hidden

    Local symbols are hidden, as described above.

  - Global and weak symbols are preemptable

    Global and weak symbols are also preemptable, that is, they may by preempted by definitions of the same name in another component.

- `STV_PROTECTED`

  A symbol defined in the current component is protected if it is visible in other components but not preemptable, meaning that any reference to such a symbol from within the defining component must be resolved to the definition in that component, even if there is a definition in another component that would preempt by the default rules.

  A symbol with STB_LOCAL binding may not have STV_PROTECTED visibility.

  If a symbol definition with STV_PROTECTED visibility from a shared object is taken as resolving a reference from an executable or another shared object, the SHN_UNDEF symbol table entry created has STV_DEFAULT visibility.

- `STV_HIDDEN`

  A symbol defined in the current component is hidden if its name is not visible to other components.

  Such a symbol is necessarily protected.

  This attribute may be used to control the external interface of a component.

  Note that an object named by such a symbol may still be referenced from another component if its address is passed outside.
A hidden symbol contained in a relocatable object must be either removed or converted to STB_LOCAL binding by the link-editor when the relocatable object is included in an executable file or shared object.

## Symbol Table Entry at Index 0

Index 0 both designates the first entry in the table and serves as the undefined symbol index.

```
Name      Value         Note
st_name   0             No name
st_value  0             Zero value
st_size   0             No size
st_info   0             No type, local binding
st_other  0             Default visibility
st_shndx  SHN_UNDEF(0)  No section
```
