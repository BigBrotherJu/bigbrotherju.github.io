# 二进制相关工具

## 编译汇编链接

- as

  汇编器，详见例17.1。

  ``` console
  as hello.s -o hello.o
  ```

- ld

  链接器，详见例17.1，用--verbose选项可以显示默认链接脚本，详见第19.1节。

  ``` console
  ld hello.o -o hello
  ```

## 读取二进制元数据

### readelf

显示 ELF 格式二进制文件中的信息。

`readelf` 的用法主要分为：

- header 相关
- elf 内容展示
- symbol table 相关
- binary archive
- dump elf 内容
- 显示相关
- demangle 相关
- debug info 相关
- 其他

``` console
$ readelf -v
GNU readelf (GNU Binutils) 2.45.0
Copyright (C) 2025 Free Software Foundation, Inc.
This program is free software; you may redistribute it under the terms of
the GNU General Public License version 3 or (at your option) any later version.
This program has absolutely no warranty.
$ readelf -H
Usage: readelf <option(s)> elf-file(s)
 Display information about the contents of ELF format files
 Options are:

  # 实际上是 -h -S -g -l -d -r -u -s -V -n (-A -I)
  -a --all               Equivalent to: -h -l -S -s -r -d -V -A -I

  # header 相关
  -h --file-header       Display the ELF file header
  -l --program-headers   Display the program headers
     --segments          An alias for --program-headers
  -S --section-headers   Display the sections' header
     --sections          An alias for --section-headers
  -g --section-groups    Display the section groups
  -t --section-details   Display the section details. Implies -S.
                         # 会把 flag 更详细显示，其他不变
  -e --headers           Equivalent to: -h -l -S

  # elf 内容展示
  -n --notes             Display the contents of note sections (if present)
  -r --relocs            Display the relocations (if present)
  -u --unwind            Display the unwind info (if present)
  -d --dynamic           Display the dynamic section (if present)
  -V --version-info      Display the version sections (if present)
  -A --arch-specific     Display architecture specific information (if any)
  -D --use-dynamic       Use the dynamic section info when displaying symbols
                         # -Ds 显示 dynamic symbols -Dr 显示 dynamic relocation
  -I --histogram         Display histogram of bucket list lengths when displaying
                         the contents of the symbol tables.
  -j --display-section=<name|number>
                         Display the contents of the indicated section.  Can be repeated

  # symbol table 相关
  -s --syms              Display the symbol table # 包括 --dyn-syms
     --symbols           An alias for --syms
     --dyn-syms          Display the dynamic symbol table
     --lto-syms          Display LTO symbol tables
     -X --extra-sym-info Display extra information when showing symbols
                         # 增加 section name，会同时开启 -W，要和上面三个 option 一起用，比如 -sX
     --no-extra-sym-info Do not display extra information when showing symbols (default)
     --sym-base=[0|8|10|16]
                         Force base for symbol sizes.  The options are
                         mixed (the default), octal, decimal, hexadecimal.
     --quiet             Suppress "no symbols" diagnostic.

  # binary archive
  -c --archive-index     Display the symbol/file index in an archive

  # dump elf 内容
  -L --lint|--enable-checks
                         Display warning messages for possible problems
  -x --hex-dump=<number|name>
                         Dump the contents of section <number|name> as bytes
  -p --string-dump=<number|name>
                         Dump the contents of section <number|name> as strings
  -R --relocated-dump=<number|name>
                         Dump the relocated contents of section <number|name>
  -z --decompress        Decompress section before dumping it

  # 显示相关
  -W --wide              Allow output width to exceed 80 characters
  -T --silent-truncation If a symbol name is truncated, do not add [...] suffix

  # demangle 相关
  -C --demangle[=STYLE]  Decode mangled/processed symbol names
                           STYLE can be "none", "auto", "gnu-v3", "java",
                           "gnat", "dlang", "rust"
     --no-demangle       Do not demangle low-level symbol names.  (default)
     --recurse-limit     Enable a demangling recursion limit.  (default)
     --recursion-limit   An alias for --recurse-limit
     --no-recurse-limit  Disable a demangling recursion limit
     --no-recursion-limitAn alias for --no-recurse-limit
     -U[dlexhi] --unicode=[default|locale|escape|hex|highlight|invalid]
                         Display unicode characters as determined by the current locale
                          (default), escape sequences, "<hex sequences>", highlighted
                          escape sequences, or treat them as invalid and display as
                          "{hex sequences}"

  # debug info 相关
  -w --debug-dump[a/=abbrev, A/=addr, r/=aranges, c/=cu_index, L/=decodedline,
                  f/=frames, F/=frames-interp, g/=gdb_index, i/=info, o/=loc,
                  m/=macro, p/=pubnames, t/=pubtypes, R/=Ranges, l/=rawline,
                  s/=str, O/=str-offsets, u/=trace_abbrev, T/=trace_aranges,
                  U/=trace_info]
                         Display the contents of DWARF debug sections
  -wk --debug-dump=links Display the contents of sections that link to separate
                          debuginfo files
  -wK --debug-dump=follow-links
                         Follow links to separate debug info files (default)
  -wN --debug-dump=no-follow-links
                         Do not follow links to separate debug info files
  -P --process-links     Display the contents of non-debug sections in separate
                          debuginfo files.  (Implies -wK)
  -wD --debug-dump=use-debuginfod
                         When following links, also query debuginfod servers (default)
  -wE --debug-dump=do-not-use-debuginfod
                         When following links, do not query debuginfod servers
  --dwarf-depth=N        Do not display DIEs at depth N or greater
  --dwarf-start=N        Display DIEs starting at offset N
  --ctf=<number|name>    Display CTF info from section <number|name>
  --ctf-parent=<name>    Use CTF archive member <name> as the CTF parent
  --ctf-parent-section=<number|name>
                         pick a completely different section for the CTF parent dictionary
  --ctf-symbols=<number|name>
                         Use section <number|name> as the CTF external symtab
  --ctf-strings=<number|name>
                         Use section <number|name> as the CTF external strtab
  --sframe[=NAME]        Display SFrame info from section NAME, (default '.sframe')

  # 其他
  @<file>                Read options from <file>
  -H --help              Display this information
  -v --version           Display the version number of readelf
Report bugs to <https://gitlab.archlinux.org/archlinux/packaging/packages/binutils/-/issues>
```

### readelf objdump 区别

- 二进制格式支持

  readelf 只支持分析 ELF，objdump 除了 ELF 还支持分析别的二进制格式。

- 适用场景

  readelf 对 ELF 的分析结果更详细，主要用来分析 ELF 文件。

  objdump 也可以分析 ELF 文件，但是主要用来进行反汇编。

- 实现方式

  readelf 不使用 BFD library，objdump 使用 BFD library。

> This program performs a similar function to objdump but it goes into more detail and it exists independently of the BFD library, so if there is a bug in BFD then readelf will not be affected.
>
> Source: readelf man page

### objdump

显示二进制文件中的信息。

`objdump` 的用法主要分为：

- mandatory option
  - disassemble 相关
  - dump 二进制内容
  - header 相关
  - symbol table 相关
  - debug info
  - 其他
- optional option
  - disassemble 相关
  - 展示信息（disassemble/dump）相关
  - 其他
  - demangle 相关
  - debug info

``` console
$ objdump -v
GNU objdump (GNU Binutils) 2.45.0
Copyright (C) 2025 Free Software Foundation, Inc.
This program is free software; you may redistribute it under the terms of
the GNU General Public License version 3 or (at your option) any later version.
This program has absolutely no warranty.
$ objdump -H
Usage: objdump <option(s)> <file(s)>
 Display information from object <file(s)>.

 # mandatory option ############################################################
 At least one of the following switches must be given:

 ## disassemble 相关
  -d, --disassemble        Display assembler contents of executable sections
  -D, --disassemble-all    Display assembler contents of all non-empty non-bss sections,
                            -j may be used to select specific sections.
                            # 所有 section 都按指令解释
      --disassemble=<sym>  Display assembler contents from <sym>
  -S, --source             Intermix source code with disassembly.
                           Implies -d. # 不用输 -dS
      --source-comment[=<txt>] Prefix lines of source code with <txt>
  -r, --reloc              Display the relocation entries in the file
                           If used with -d or -D, the relocations are printed interspersed
                           with the disassembly.
  -R, --dynamic-reloc      Display the dynamic relocation entries in the file
                           If used with -d or -D, the relocations are printed interspersed
                           with the disassembly.
                           Note: objdump does not support displaying RELR type relocations.
                           These can be displayed by the readelf program.

  ## dump 二进制内容
  -s, --full-contents      Display the full contents of all sections requested,
                           often used in combination with -j to request specific sections.
                           By default all non-empty non-bss sections are displayed.
  -Z, --decompress         Decompress section(s) before displaying their contents
                           The -Z option is meant to be used in conunction with the -s option

  ## header 相关
  -a, --archive-headers    Display archive header information
  -f, --file-headers       Display the contents of the overall file header
  -p, --private-headers    Display object format specific file header contents
  -P, --private=OPT,OPT... Display object format specific contents
  -h, --[section-]headers  Display the contents of the section headers
  -x, --all-headers        Display the contents of all headers
                           Using -x is equivalent to specifying all of -a -f -h -p -r -t.

  ## symbol table 相关
  -t, --syms               Display the contents of the symbol table(s)
  -T, --dynamic-syms       Display the contents of the dynamic symbol table

  ## debug info
  -g, --debugging          Display debug information in object file
  -e, --debugging-tags     Display debug information using ctags style
  -G, --stabs              Display (in raw form) any STABS info in the file
  -W, --dwarf[a/=abbrev, A/=addr, r/=aranges, c/=cu_index, L/=decodedline,
              f/=frames, F/=frames-interp, g/=gdb_index, i/=info, o/=loc,
              m/=macro, p/=pubnames, t/=pubtypes, R/=Ranges, l/=rawline,
              s/=str, O/=str-offsets, u/=trace_abbrev, T/=trace_aranges,
              U/=trace_info]
                           Display the contents of DWARF debug sections
  -Wk,--dwarf=links        Display the contents of sections that link to
                            separate debuginfo files
  -WK,--dwarf=follow-links
                           Follow links to separate debug info files (default)
  -WN,--dwarf=no-follow-links
                           Do not follow links to separate debug info files
  -WD --dwarf=use-debuginfod
                           When following links, also query debuginfod servers (default)
  -WE --dwarf=do-not-use-debuginfod
                           When following links, do not query debuginfod servers
  -L, --process-links      Display the contents of non-debug sections in
                            separate debuginfo files.  (Implies -WK)
      --ctf[=SECTION]      Display CTF info from SECTION, (default `.ctf')
      --sframe[=SECTION]   Display SFrame info from SECTION, (default '.sframe')

  ## 其他
  @<file>                  Read options from <file>
  -v, --version            Display this program's version number
  -i, --info               List object formats and architectures supported
  -H, --help               Display this information

 # optional option #############################################################
 The following switches are optional:

 ## disassemble 相关
      --file-start-context       Include context from start of file (with -S)
  -l, --line-numbers             Include line numbers and filenames in output,
                                  Only useful with -d, -D, or -r.
      --inlines                  Print all inlines for source line (with -l)
      --show-all-symbols         When disassembling, display all symbols at a given address
  -z, --disassemble-zeroes       Do not skip blocks of zeroes when disassembling

 ### 处理 source file 查找
  -I, --include=DIR              Add DIR to search list for source files
      --prefix=PREFIX            Add PREFIX to absolute paths for -S
      --prefix-strip=LEVEL       Strip initial directory names for -S

 ### 指令相关
      --[no-]show-raw-insn       Display hex alongside symbolic disassembly
      --insn-width=WIDTH         Display WIDTH bytes on a single line for -d

 ### 地址相关
      --no-addresses             Do not print address alongside disassembly
      --prefix-addresses         Print complete address alongside disassembly

 ### disassembler options
  -M, --disassembler-options=OPT Pass text OPT on to the disassembler

  For RISC-V, the following options are supported:

  max
  Disassemble without checking architecture string. This is a best effort mode,
  so for overlapping ISA extensions the first match (possibly incorrect in a given context)
  will be used to decode the instruction. It’s useful, if the ELF file doesn’t expose ISA
  string, preventing automatic ISA subset deduction, and the default fallback ISA string
  (rv64gc) doesn’t cover all instructions in the binary.

  numeric
  Print numeric register names, rather than ABI names (e.g., print x2 instead of sp).

  no-aliases
  Disassemble only into canonical instructions. For example, compressed instructions
  will be represented as such (addi sp,sp,-128 will be c.addi16sp sp,-128).

  priv-spec=SPEC
  Print the CSR according to the chosen privilege spec version (e.g., 1.10, 1.11, 1.12, 1.13).

 ### 显示相关
      --visualize-jumps          Visualize jumps by drawing ASCII art lines
      --visualize-jumps=color    Use colors in the ASCII art
      --visualize-jumps=extended-color
                                 Use extended 8-bit color codes
      --visualize-jumps=off      Disable jump visualization

      --disassembler-color=off       Disable disassembler color output.
      --disassembler-color=terminal  Enable disassembler color output if displaying on a terminal. (default)
      --disassembler-color=on        Enable disassembler color output.
      --disassembler-color=extended  Use 8-bit colors in disassembler output.

  -w, --wide                     Format output for more than 80 columns

 ## 展示信息（disassemble/dump）相关
  -j, --section=NAME             Only display information for section NAME
  -F, --file-offsets             Include file offsets when displaying information,
                                 which is disassembling or dumping.
      --start-address=ADDR       Only process data whose address is >= ADDR
                                 This affects the output of the -d, -r and -s options.
      --stop-address=ADDR        Only process data whose address is < ADDR
                                 This affects the output of the -d, -r and -s options.
      --adjust-vma=OFFSET        Add OFFSET to all displayed section addresses
      --special-syms             Include special symbols in symbol dumps

 ## 其他
  -b, --target=BFDNAME           Specify the target object format as BFDNAME
  -m, --architecture=MACHINE     Specify the target architecture as MACHINE
  -EB --endian=big               Assume big endian format when disassembling
  -EL --endian=little            Assume little endian format when disassembling

 ## demangle 相关
  -C, --demangle[=STYLE]         Decode mangled/processed symbol names
                                   STYLE can be "none", "auto", "gnu-v3",
                                   "java", "gnat", "dlang", "rust"
      --recurse-limit            Enable a limit on recursion whilst demangling
                                  (default)
      --recursion-limit          An alias for --recurse-limit
      --no-recurse-limit         Disable a limit on recursion whilst demangling
      --no-recursion-limit       An alias for --no-recurse-limit
  -U[d|l|i|x|e|h]                Controls the display of UTF-8 unicode characters
  --unicode=[default|locale|invalid|hex|escape|highlight]

 ## debug info
      --dwarf-depth=N            Do not display DIEs at depth N or greater
      --dwarf-start=N            Display DIEs starting at offset N
      --dwarf-check              Make additional dwarf consistency checks.
      --ctf-parent=NAME          Use CTF archive member NAME as the CTF parent
      --ctf-parent-section[=SECTION]
                                 Pick a completely different section for the CTF parent dictionary

objdump: supported targets: elf64-x86-64 elf32-i386 elf32-iamcu elf32-x86-64 pei-i386 pe-x86-64 pei-x86-64 elf64-little elf64-big elf32-little elf32-big pe-bigobj-x86-64 pe-i386 pdb elf64-bpfle elf64-bpfbe srec symbolsrec verilog tekhex binary ihex plugin
objdump: supported architectures: i386 i386:x86-64 i386:x64-32 i8086 i386:intel i386:x86-64:intel i386:x64-32:intel iamcu iamcu:intel bpf xbpf

The following i386/x86-64 specific disassembler options are supported for use
with the -M switch (multiple options should be separated by commas):
  x86-64      Disassemble in 64bit mode
  i386        Disassemble in 32bit mode
  i8086       Disassemble in 16bit mode
  att         Display instruction in AT&T syntax
  intel       Display instruction in Intel syntax
  att-mnemonic  (AT&T syntax only)
              Display instruction with AT&T mnemonic
  intel-mnemonic  (AT&T syntax only)
              Display instruction with Intel mnemonic
  addr64      Assume 64bit address size
  addr32      Assume 32bit address size
  addr16      Assume 16bit address size
  data32      Assume 32bit data size
  data16      Assume 16bit data size
  suffix      Always display instruction suffix in AT&T syntax
  amd64       Display instruction in AMD64 ISA
  intel64     Display instruction in Intel64 ISA

The following BPF specific disassembler options are supported for use
with the -M switch (multiple options should be separated by commas):

      pseudoc                  Use pseudo-c syntax.
      v1,v2,v3,v4,xbpf         Version of the BPF ISA to use.
      hex,oct,dec              Output numerical base for immediates.

Options supported for -P/--private switch:
For PE files:
  header      Display the file header
  sections    Display the section headers
Report bugs to <https://gitlab.archlinux.org/archlinux/packaging/packages/binutils/-/issues>.
```

### nm

  查看符号表，详见第18.2节。

  ``` console
  nm /usr/lib/crt1.o
  ```

- strip

  去除可执行文件中的符号信息，详见第17.5.2节。

  ``` console
  strip max
  ```

## 库/Library

- ldd

  用动态链接器测试一个程序依赖于哪些共享库，并查找这些共享库都在什么路径下，详见第19.4节。

- ar

  把目标文件打包成静态库，详见第19.3节。

- ranlib

  给ar打包的静态库建索引，详见第19.3节。

## 二进制查看工具

- od

  另一种二进制文件查看工具，以八进制、十六进制或ASCII字符显示一个文件，详见第24.2.1节。

- hexdump

  二进制文件查看工具，以十六进制或ASCII字符显示一个文件，详见第17.5.1节。

  ``` console
  hd max.o
  ```
