# Cross-Compile perf for RISC-V

https://medium.com/@manas.marwah/building-perf-tool-fc838f084f71

https://perfwiki.github.io/main/development/

https://perfwiki.github.io/main/arm64-cross-compilation-dockerfile/

`linux-6.16-rc3/tools/perf/Documentation/Build.txt`

## Option perf support

The standard Linux distribution package for the perf tool includes only basic support, lacking the full array of options.

```
$ perf --version --build-options
perf version 6.15-1
                   aio: [ on  ]  # HAVE_AIO_SUPPORT
                   bpf: [ on  ]  # HAVE_LIBBPF_SUPPORT
         bpf_skeletons: [ on  ]  # HAVE_BPF_SKEL
            debuginfod: [ on  ]  # HAVE_DEBUGINFOD_SUPPORT
                 dwarf: [ on  ]  # HAVE_LIBDW_SUPPORT
    dwarf_getlocations: [ on  ]  # HAVE_LIBDW_SUPPORT
          dwarf-unwind: [ on  ]  # HAVE_DWARF_UNWIND_SUPPORT
              auxtrace: [ on  ]  # HAVE_AUXTRACE_SUPPORT
                libbfd: [ OFF ]  # HAVE_LIBBFD_SUPPORT
           libcapstone: [ OFF ]  # HAVE_LIBCAPSTONE_SUPPORT
             libcrypto: [ on  ]  # HAVE_LIBCRYPTO_SUPPORT
    libdw-dwarf-unwind: [ on  ]  # HAVE_LIBDW_SUPPORT
                libelf: [ on  ]  # HAVE_LIBELF_SUPPORT
               libnuma: [ on  ]  # HAVE_LIBNUMA_SUPPORT
            libopencsd: [ OFF ]  # HAVE_CSTRACE_SUPPORT
               libperl: [ on  ]  # HAVE_LIBPERL_SUPPORT
               libpfm4: [ on  ]  # HAVE_LIBPFM
             libpython: [ on  ]  # HAVE_LIBPYTHON_SUPPORT
              libslang: [ on  ]  # HAVE_SLANG_SUPPORT
         libtraceevent: [ on  ]  # HAVE_LIBTRACEEVENT
             libunwind: [ OFF ]  # HAVE_LIBUNWIND_SUPPORT
                  lzma: [ on  ]  # HAVE_LZMA_SUPPORT
numa_num_possible_cpus: [ on  ]  # HAVE_LIBNUMA_SUPPORT
                  zlib: [ on  ]  # HAVE_ZLIB_SUPPORT
                  zstd: [ on  ]  # HAVE_ZSTD_SUPPORT
```

## Cross-Compile

```
4) Cross compilation
====================
As Multiarch is commonly supported in Linux distributions, we can install
libraries for multiple architectures on the same system and then cross-compile
Linux perf. For example, Aarch64 libraries and toolchains can be installed on
an x86_64 machine, allowing us to compile perf for an Aarch64 target.

Below is the command for building the perf with dynamic linking.

  $ cd /path/to/Linux
  $ make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C tools/perf

For static linking, the option `LDFLAGS="-static"` is required.

  $ make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    LDFLAGS="-static" -C tools/perf

In the embedded system world, a use case is to explicitly specify the package
configuration paths for cross building:

  $ PKG_CONFIG_SYSROOT_DIR="/path/to/cross/build/sysroot" \
    PKG_CONFIG_LIBDIR="/usr/lib/:/usr/local/lib" \
    make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C tools/perf

In this case, the variable PKG_CONFIG_SYSROOT_DIR can be used alongside the
variable PKG_CONFIG_LIBDIR or PKG_CONFIG_PATH to prepend the sysroot path to
the library paths for cross compilation.

source: tools/perf/Documentation/Build.txt
```

- 搞一个 ubuntu docker

  `sudo docker run -it --rm -v "$(pwd)":/usr/src/linux ubuntu:25.10 bash`

  `pwd` 指 linux 源代码根目录。

  25.04 可以编译出动态链接的 perf，因为提供的 libelf-dev 包的版本问题，编译静态链接的 perf 会出错。详细见下面。

- `dpkg --add-architecture riscv64`

- 更改 `/etc/apt/sources.list.d/ubuntu.sources`

  如果用 25.04，下面的 `questing` 要改成 `plucky`。

  给已经存在的两个条目加上 `Architectures: amd64`，另外再增加 riscv 的源：

  ```
  sed -i '/Signed-By:/a Architectures: amd64' /etc/apt/sources.list.d/ubuntu.sources

  cat >> /etc/apt/sources.list.d/ubuntu.sources << 'EOF'

  Types: deb
  URIs: http://ports.ubuntu.com/ubuntu-ports
  Suites: questing questing-updates questing-backports
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
  Architectures: riscv64

  Types: deb
  URIs: http://ports.ubuntu.com/ubuntu-ports
  Suites: questing-security
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
  Architectures: riscv64
  EOF
  ```

- `apt update`

- 安装 native build package

  ```
  apt install make flex bison pkg-config \
  python3 python3-dev python3-setuptools \
  gcc-riscv64-linux-gnu
  ```

- 安装 riscv perf 依赖

  ```
  apt install \
  libaudit-dev:riscv64 \
  libaio-dev:riscv64 \
  libbabeltrace-dev:riscv64 \
  libbison-dev:riscv64 \
  libbz2-dev:riscv64 \
  libcap-dev:riscv64 \
  libcapstone-dev:riscv64 \
  libdebuginfod-dev:riscv64 \
  libdw-dev:riscv64 \
  libdwarf-dev:riscv64 \
  libelf-dev:riscv64 \
  libfl-dev:riscv64 \
  libiberty-dev:riscv64 \
  liblzma-dev:riscv64 \
  libnuma-dev:riscv64 \
  libperl-dev:riscv64 \
  libpfm4-dev:riscv64 \
  libpython3-dev:riscv64 \
  libslang2-dev:riscv64 \
  libssl-dev:riscv64 \
  libtraceevent-dev:riscv64 \
  libtracefs-dev:riscv64 \
  libunwind-dev:riscv64 \
  libzstd-dev:riscv64 \
  systemtap-sdt-dev:riscv64
  ```

- 编译动态链接的 perf（推荐）

  makefile 会自己设置 `PKG_CONFIG_LIBDIR` 包含 `/usr/lib/riscv64-linux-gnu/pkgconfig`，不需要人工干预。

  25.04 没问题。25.10 没问题。

  ```
  make -C tools/perf clean &&
  make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -C tools/perf
  ```

  动态链接的 perf 还需要 dynamic linker 和 shared object 才能工作。如果 linux rootfs 里没有这些，最省事的方式是直接把 docker 里的 `/usr/lib/riscv64-linux-gnu` 整个文件夹一起复制到 rootfs 里并命名为 `/lib`。`perf` 也要复制。

  有一个问题是 dynamic linker 实际上有两个：

  ```
  (docker) ls -al $(find . -name ld-linux-riscv64-lp64d.so.1)
  lrwxrwxrwx 1 root root     45 May 22 03:11 ./usr/lib/ld-linux-riscv64-lp64d.so.1 -> riscv64-linux-gnu/ld-linux-riscv64-lp64d.so.1
  -rwxr-xr-x 1 root root 153048 May 22 03:11 ./usr/lib/riscv64-linux-gnu/ld-linux-riscv64-lp64d.so.1
  -rwxr-xr-x 1 root root 152136 Mar 21 16:57 ./usr/riscv64-linux-gnu/lib/ld-linux-riscv64-lp64d.so.1
  ```

  实际测试下来 `/usr/lib/riscv64-linux-gnu/ld-linux-riscv64-lp64d.so.1` 没有问题。

- 编译静态链接的 perf（不推荐）

  25.04 有问题。如果静态编译，ubuntu plucky 25.04 提供的 libelf-dev 包有问题，`/usr/lib/riscv64-linux-gnu/libelf.a` 里面没有 `eu_search_tree_init` 和 `eu_search_tree_fini` 定义，静态编译会出错，必须使用 25.10。25.10 提供的 libelf-dev 包版本更新，解决了这个问题。

  https://sourceware.org/bugzilla/show_bug.cgi?id=32293

  25.10 可以编译出来 perf，但是有两个问题。一是编译的时候已经安装了一些 lib，但是 make 检测不到：

  ```
  Makefile.config:564: No elfutils/debuginfod.h found, no debuginfo server support, please install libdebuginfod-dev/elfutils-debuginfod-client-devel or equivalent
  Makefile.config:694: Warning: Disabled BPF skeletons as clang (clang) is missing
  Makefile.config:777: No libcrypto.h found, disables jitted code injection, please install openssl-devel or libssl-dev
  Makefile.config:876: No 'Python.h' was found: disables Python support - please install python-devel/python-dev
  Makefile.config:968: No libllvm 13+ found, slower source file resolution, please install llvm-devel/llvm-dev
  Makefile.config:1086: No libbabeltrace found, disables 'perf data' CTF format support, please install libbabeltrace-dev[el]/libbabeltrace-ctf-dev
  Makefile.config:1129: No alternatives command found, you need to set JDIR= to point to the root of your Java directory
  ```

  二是编译出来的二进制实际上还是需要 shared object 才能工作。编译时的部分 warning 如下：

  ```
  /usr/lib/gcc-cross/riscv64-linux-gnu/14/../../../../riscv64-linux-gnu/bin/ld: libperf-util.a(perf-util-in.o): in function `dlfilter__new':
  (.text+0xd24f2): warning: Using 'dlopen' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
  /usr/lib/gcc-cross/riscv64-linux-gnu/14/../../../../riscv64-linux-gnu/bin/ld: /usr/lib/riscv64-linux-gnu/libperl.a(pp_sys.o): in function `Perl_pp_ehostent':
  (.text+0xcb1a): warning: Using 'setgrent' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
  ```

  ```
  make -C tools/perf clean &&
  make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- LDFLAGS="-static" -C tools/perf
  ```
