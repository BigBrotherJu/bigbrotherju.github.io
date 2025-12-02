---
title: RISC-V Board
date: 2025-05-31 20:30:00 +0800
categories: [Embedded Systems]
tags: [embedded systems, risc-v]
---

RISC-V 作为一种新颖的指令集，近年来在工业界开始逐渐流行。本文主要对市场上流行的 RISC-V SOC 和单片机进行盘点汇总。

在嵌入式开发领域，产品的层级主要有三层：开发板（也叫单片机、板卡）、SOC、CPU。SOC 包含了 CPU 和其他一些模块，比如音频模块、视频模块、内存。开发板主要是放置一些物理接口，并把对应的线路与 SOC 芯片的引脚相连。

针对一个 SOC，不同的厂商可能会推出不同的开发板。所以，本文大致按时间顺序从新到旧列出 SOC，并将使用同一 SOC 的开发板列在一起。

以下的 SOC 中，算能和迭代时空正在努力向 Linux 上游提交 patch，详细见：

https://github.com/spacemit-com/linux/wiki

https://github.com/sophgo/linux/wiki

## 汇总表格

| CPU | 备注 | SOC | 备注 | 开发板 | 备注 |
| --- | --- | --- | ---  | ---   | --- |
| [SiFive P550][P550] | 3 发射乱序 13 级流水线 | ESWIN EIC7700X | 4 核 P550 | [Milk-V Megrez][megrez] | |
| SiFive P550 | 3 发射乱序 13 级流水线 | ESWIN EIC7700X | 4 核 P550 | [SiFive HiFive Premier P550][sf-p550-board] | |
| SiFive P550 | 3 发射乱序 13 级流水线 | ESWIN EIC7700X | 4 核 P550 | [Pine64 STARPro64][starpro64] | |
| [迭代时空 X60][X60] | 2 发射顺序 8 级流水线 | [迭代时空 K1][K1] | 8 核 CPU | [Milk-V Jupiter][jupiter] |  |
| 迭代时空 X60 | 2 发射顺序 8 级流水线 | 迭代时空 K1 | 8 核 CPU | [香蕉派 F3][bpi-f3] |  |
| 迭代时空 X60 | 2 发射顺序 8 级流水线 | 迭代时空 K1 | 8 核 CPU | [矽速科技 LicheePi 3A][licheepi-3a] |  |
| [达摩院玄铁 C920][C920] | 多发射乱序 12 级流水线 | [算能 SG2042][SG2042] | 64 核 C920 | [Milk-V Pioneer][pioneer] |  |
| [达摩院玄铁 C910][C910] | 3 发射乱序 12 级流水线 | 平头哥 曳影 1520 | 4 核 C910，SOC 没有产品页面 | [Milk-V Meles][meles] |  |
| 达摩院玄铁 C910 | 3 发射乱序 12 级流水线 | 平头哥 曳影 1520 | 4 核 C910 | [矽速科技 LicheePi 4A][licheepi-4a] |  |
| 达摩院玄铁 C910 | 3 发射乱序 12 级流水线 | 平头哥 曳影 1520 | 4 核 C910 | [BeagleV-Ahead][beaglev-ahead] | |
| [达摩院玄铁 C906][C906] | 顺序 5 级流水线 | [算能 晶视 CV1800B][CV1800B] | 双核 C906，无缓存一致性  | [Milk-V Duo][duo] |  |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | [算能 SG2002][SG200x] | 双核 C906，无缓存一致性；ARM Cortex-A53 | [Milk-V Duo 256M][duo] | 内存 256 MB |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | 算能 SG2002 | 双核 C906，无缓存一致性；ARM Cortex-A53 | [矽速科技 LicheeRV Nano][licheerv-nano] | 内存 256 MB |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | [算能 SG2000][SG200x] | 双核 C906，无缓存一致性；ARM Cortex-A53 | [Milk-V Duo S][duo] | 内存 512 MB |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | [全志 D1-H][D1H] | 单核 C906 | [全志 D1-H 哪吒开发板][nezha] | |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | 全志 D1-H | 单核 C906 | [东山派 哪吒 STU][dongshan-nezha] | 有绿色、蓝色、红色 |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | 全志 D1-H | 单核 C906 | [矽速科技 LicheePi RV Dock][licheerv-dock] | |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | [全志 D1s][D1s] | 单核 C906 | [全志 D1s 哪吒开发板][nezha-d1s] | |
| 达摩院玄铁 C906 | 顺序 5 级流水线 | 全志 D1s | 单核 C906 | [东山派 D1s][dongshan-d1s] | |
| [SiFive U74][U74]   | 2 发射顺序 8 级流水线 | [赛昉科技 昉·惊鸿 7110][sf-soc] | 4 核 U74 | [Milk-V Mars][mars] | |
| SiFive U74 | 2 发射顺序 8 级流水线 | 赛昉科技 昉·惊鸿 7110 | 4 核 U74 | [Pine64 STAR64][star64] |  |
| SiFive U74 | 2 发射顺序 8 级流水线 | 赛昉科技 昉·惊鸿 7110 | 4 核 U74 | [赛昉 昉·星光 2][sf-board] |  |
| SiFive U74 | 2 发射顺序 8 级流水线 | [赛昉科技 昉·惊鸿 7100][sf-soc] | 2 核 U74 | [赛昉 昉·星光][sf-board] |  |

[X60]: https://www.spacemit.com/spacemit-x60-core/
[P550]: https://www.sifive.com/cores/performance-p500
[U74]: https://www.sifive.com/cores/essential-7
[C920]: https://www.xrvm.cn/product/xuantie/C920
[C910]: https://www.xrvm.cn/product/xuantie/C910
[C906]: https://www.xrvm.cn/product/xuantie/C906

[sf-soc]: https://www.starfivetech.com/site/soc
[K1]: https://www.spacemit.com/key-stone-k1/
[CV1800B]: https://www.sophgo.com/sophon-u/product/introduce/cv180xb.html
[SG200x]: https://www.sophgo.com/sophon-u/product/introduce/sg200x.html
[SG2042]: https://www.sophgo.com/sophon-u/product/introduce/sg2042.html
[D1H]: https://www.aw-ol.com/chips/1
[D1s]: https://www.aw-ol.com/chips/5

[dongshan-d1s]: https://dongshanpi.com/DongshanPI-D1s/01-BoardIntroduction/
[dongshan-nezha]: https://dongshanpi.com/DongshanNezhaSTU/01-BoardIntroduction/
[nezha]: https://d1.docs.aw-ol.com/d1_dev/
[nezha-d1s]: https://d1s.docs.aw-ol.com/hard/hard_1board/
[licheepi-4a]: https://wiki.sipeed.com/hardware/zh/lichee/th1520/lpi4a/1_intro.html
[licheepi-3a]: https://wiki.sipeed.com/hardware/zh/lichee/K1/lpi3a/1_intro.html
[licheerv-dock]: https://wiki.sipeed.com/hardware/zh/lichee/RV/Dock.html
[licheerv-nano]: https://wiki.sipeed.com/hardware/zh/lichee/RV_Nano/1_intro.html
[sf-p550-board]: https://www.sifive.com/boards/hifive-premier-p550
[bpi-f3]: https://www.banana-pi.org.cn/zh-banana-pi-sbcs/175.html
[star64]: https://pine64.com/product-category/star64/
[sf-board]: https://www.starfivetech.com/site/boards
[duo]:https://milkv.io/zh/duo
[pioneer]: https://milkv.io/zh/pioneer
[mars]: https://milkv.io/zh/mars
[meles]: https://milkv.io/zh/meles
[jupiter]: https://milkv.io/zh/jupiter
[megrez]: https://milkv.io/zh/megrez
[beaglev-ahead]: https://www.beagleboard.org/boards/beaglev-ahead
[starpro64]: https://pine64.com/product/starpro64-32gb-single-board-computer/

## 开源情况

Fedora by Fedora-V Force 基本所有板子都支持。

- ESWIN EIC7700X

  - Milk-V Megrez

    https://milkv.io/zh/docs/megrez/getting-started/resources

    - Debian/RockOS

      https://github.com/milkv-megrez

      https://github.com/orgs/rockos-riscv/repositories?type=all

      https://rockos-riscv.github.io/rockos-docs/

      不清楚完整 build 流程，只有二进制。

    - Fedora by Fedora-V Force

  - SiFive HiFive Premier P550

    16G 399 USD，32G 499 USD 太贵了。国内也有卖，这个可以。

    https://forums.sifive.com/t/how-to-compile-and-install-kernel/6836

    https://github.com/sifiveinc/riscv-linux/commits/rel/kernel/hifive-premier-p550

    https://github.com/sifiveinc/hifive-premier-p550-ubuntu/releases

    可以用官方提供的 ubuntu，只需要把内核换了就可以。

  - Pine64 STARPro64

    只能跑 RockOS。

- 迭代时空 K1

  https://bianbu.spacemit.com/en/development/perf

  https://bianbu-linux.spacemit.com/source

  - MUSE Pi Pro
  - MUSE Card

- 平头哥 曳影 1520

  RevyOS 支持下面的三个设备。

  https://github.com/revyos

  https://docs.revyos.dev/

  - Milk-V Meles

  - 矽速科技 LicheePi 4A

    矽速科技还有自己的镜像

  - Beagle-Ahead

    他自己的 SDK 完全开源。

- 算能 SG2042

  - Milk-V Pioneer

    貌似可以直接跑 upstream Linux。

## 嘉楠 勘智 K510 双核不知名 CPU

https://www.canaan-creative.com/product/%E5%8B%98%E6%99%BAk510

- 嘉楠 勘智 K510 CRB-KIT 开发者套装

  https://www.canaan-creative.com/product/canaan-k510-crb

- 百问科技

  https://www.100ask.net/hard/DongshanPI-Vision_Introduce

## 嘉楠 勘智 K230 双核平头哥 C908

https://www.canaan-creative.com/product/k230

- 嘉楠 K230 开发板

  https://www.canaan-creative.com/product/k230

## 嘉楠 勘智 K210 双核不知名 CPU

https://www.canaan-creative.com/product/kendryteai

这个 SOC 非常老了，不推荐
