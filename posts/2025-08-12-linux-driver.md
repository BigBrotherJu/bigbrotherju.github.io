# Linux Driver Notes

v6.16-rc3

## Device Tree

### Get Device Tree Information in Linux

`/sys/firmware/fdt` 是 DTB；`/sys/firmware/devicetree` 以目录结构程现 dtb 文件, 根节点对应 base 目录, 每一个节点对应一个目录, 每一个属性对应一个文件。

```
$ ls /sys/firmware/
devicetree fdt
```

## Platform Device

### `struct platform_device`/`struct platform_driver`

```c
// include/linux/platform_device.h

struct platform_device {
	const char	*name;
	int		id;
	bool		id_auto;
	struct device	dev;
	u64		platform_dma_mask;
	struct device_dma_parameters dma_parms;
	u32		num_resources;
	struct resource	*resource;

	const struct platform_device_id	*id_entry;
	/*
	 * Driver name to force a match.  Do not set directly, because core
	 * frees it.  Use driver_set_override() to set or clear it.
	 */
	const char *driver_override;

	/* MFD cell pointer */
	struct mfd_cell *mfd_cell;

	/* arch specific additions */
	struct pdev_archdata	archdata;
};

struct platform_driver {
	int (*probe)(struct platform_device *);
	void (*remove)(struct platform_device *);
	void (*shutdown)(struct platform_device *);
	int (*suspend)(struct platform_device *, pm_message_t state);
	int (*resume)(struct platform_device *);
	struct device_driver driver;
	const struct platform_device_id *id_table;
	bool prevent_deferred_probe;
	/*
	 * For most device drivers, no need to care about this flag as long as
	 * all DMAs are handled through the kernel DMA API. For some special
	 * ones, for example VFIO drivers, they know how to manage the DMA
	 * themselves and set this flag so that the IOMMU layer will allow them
	 * to setup and manage their own I/O address space.
	 */
	bool driver_managed_dma;
};
```

### Get Platform Device Information in Linux

`/sys/devices/platform` 含有注册进内核的所有 platform_device。

一个设备对应一个目录，进入某个目录后，如果它有 driver 子目录，表示这个 platform_device 跟某个 platform_driver 配对了。

比如下面的结果中，平台设备 `ff8a0000.i2s` 已经跟平台驱动 `rockchip-i2s` 配对了：

```
[/sys/devices/platform/ff8a0000.i2s]# ls driver -ld
lrwxrwxrwx 1 root root 0 Jan 18 16:28 driver -> ../../../bus/platform/drivers/rockchip-i2s
```

### Get Platform Driver Information in Linux

`/sys/bus/platform/drivers` 含有注册进内核的所有 platform_driver。

一个 driver 对应一个目录，进入某个目录后，如果它有配对的设备，可以直接看到。

比如下面的结果中，平台驱动 `rockchip-i2s` 跟 2 个平台设备 `ff890000.i2s` `ff8a0000.i2s` 配对了：

```
[/sys/bus/platform/drivers/rockhip-i2s]# ls
bind ff890000.i2s ff8a0000.i2s uevent unbind
```

### Conversion from DTB to `struct platform_device`

1.  内核解析 dtb 文件，把每一个节点都转换为 device_node 结构体；
2.  对于某些 device_node 结构体，会被转换为 platform_device 结构体。

#### Step 1: unflatten_device_tree()

It takes the raw, flat binary DTB provided by the bootloader and converts it into a live, in-memory tree of `struct device_node` objects.

At this point, no `platform_devices` exist yet; the kernel just has a direct representation of the DTB data.

另一篇文章已经讨论过。

根节点被保存在全局变量 `of_root` 中，从 `of_root` 开始可以访问到任意节点。

#### Step 2: of_platform_default_populate_init()

- 调用链

需要注意的是，`of_platform_default_populate_init()` 是 arch_initcall，大部分 platform driver 的 init 函数是 device_initcall。所以在 `of_platform_default_populate_init()` 执行的时候，platform bus 上没有 driver，`__device_attach()` 中的对每个 driver 调用 `__device_attach_driver()` 无法实现。所以下面的调用链只能执行到 `__device_attach()`。

```
of_platform_default_populate_init
    of_platform_default_populate
        of_platform_populate
            of_platform_bus_create // 对设备树里每个可以成为 platform dev 的设备，调用 ...pdata
                of_platform_device_create_pdata
                    of_device_alloc  // （代码不在下面）分配，初始化 platform device
                    of_device_add    // 把 platform device 注册到内核中
                        device_add
                            bus_add_device    // （代码不在下面）把 device 放入全局链表
                            bus_probe_device  // 找到对应的 driver 调用 probe 函数
                                device_initial_probe
                                    __device_attach // 对每个 driver 调用 __device_attach_driver
                                        __device_attach_driver
                                            driver_match_device(drv, dev) // 判断drv dev是否匹配
                                                platform_match
                                            driver_probe_device(drv, dev) // （代码不在下面）如果匹配，调用 probe
```

---

- 哪些 device_node 结构体会被转换为 platform_device 结构体？

主要看 `of_platform_bus_create()`。

总结起来，遍历根节点的所有子节点。如果子节点有 compatible 属性，先创建 `struct platform_device`。然后把子节点的 compatible 属性值和 `"simple-bus", "simple-mfd", "isa", "arm,amba-bus"` 比较。如果匹配上了，那么把上述过程递归执行；如果匹配不上，不进行别的操作。

比如以下的节点中： `/mytest` 会被转换为 platform_device; 它的子节点 `/mytest/mytest@0` 也会被转换为 platform_device，因为该节点的父节点兼容 `"simple-bus"`。

`/i2c` 节点一般表示 i2c 控制器, 它会被转换为 platform_device, 在内核中有对应的 platform_driver; `/i2c/at24c02` 节点不会被转换为 platform_device, 它被如何处理完全由父节点的 platform_driver 决定, 一般是被创建为一个 i2c_client。

类似的也有 `/spi` 节点, 它一般也是用来表示 SPI 控制器, 它会被转换为 platform_device, 在内核中有对应的 platform_driver; `/spi/flash@0` 节点不会被转换为 platform_device, 它被如何处理完全由父节点的 platform_driver 决定, 一般是被创建为一个 spi_device。

```
/{
	mytest {
		compatile = "mytest", "simple-bus";
		mytest@0 {
			compatile = "mytest_0";
		};
	};

	i2c {
		compatile = "samsung,i2c";
		at24c02 {
			compatile = "at24c02";
		};
	};

	spi {
		compatile = "samsung,spi";
		flash@0 {
			compatible = "winbond,w25q32dw";
			spi-max-frequency = <25000000>;
			reg = <0>;
		};
	};
};
```

---

- device_node 结构体如何被转换为 platform_device 结构体？

主要看 `of_device_alloc()`。

总结起来：

- platform_device 中含有 resource 数组, 它来自 device_node 的 reg, interrupts 属性;

- platform_device.dev.of_node 指向 device_node, 可以通过它获得其他属性

---

- 生成的 platform_device 存在哪里？

主要看 `bus_add_device()`。

`device_add()` adds the device to the list of devices managed by its bus type (platform_bus_type).

the platform_device structures are "saved" by being added to a global list within the platform_bus_type structure.

---

- 没有转换为 platform_device 的节点，如何使用？

任意驱动程序里，都可以用函数直接访问设备树。

##### of_platform_default_populate_init()

`of_platform_default_populate_init` is registered with `arch_initcall_sync`. `arch_initcall_sync` registers the function `of_platform_default_populate_init` to be run as part of the `arch_initcall` sequence, which happens after core subsystems are ready but before most device drivers are probed.

```c
// drivers/of/platform.c

static int __init of_platform_default_populate_init(void)
{
	struct device_node *node;

	device_links_supplier_sync_state_pause();

	if (IS_ENABLED(CONFIG_PPC)) {
		...
	} else {
		/*
		 * Handle certain compatibles explicitly, since we don't want to create
		 * platform_devices for every node in /reserved-memory with a
		 * "compatible",
		 */
		// 先处理这些 reserved memory region
		for_each_matching_node(node, reserved_mem_matches)
			of_platform_device_create(node, NULL, NULL);

		// This part looks for a top-level /firmware node.
		// If it exists, it calls of_platform_populate on it.
		// This recursively creates platform devices for all
		// children under the /firmware node, which is a standard
		// way to group firmware-related devices like EFI or OP-TEE.
		node = of_find_node_by_path("/firmware");
		if (node) {
			of_platform_populate(node, NULL, NULL, NULL);
			of_node_put(node);
		}

		// 如果 /chosen node 里有 simple-framebuffer，进行处理
		node = of_get_compatible_child(of_chosen, "simple-framebuffer");
		if (node) {
			/*
			 * Since a "simple-framebuffer" device is already added
			 * here, disable the Generic System Framebuffers (sysfb)
			 * to prevent it from registering another device for the
			 * system framebuffer later (e.g: using the screen_info
			 * data that may had been filled as well).
			 *
			 * This can happen for example on DT systems that do EFI
			 * booting and may provide a GOP handle to the EFI stub.
			 */
			sysfb_disable(NULL);
			of_platform_device_create(node, NULL, NULL);
			of_node_put(node);
		}

		// 最重要的一步
		/* Populate everything else. */
		of_platform_default_populate(NULL, NULL, NULL);
	}

	return 0;
}
arch_initcall_sync(of_platform_default_populate_init);
```

##### 辅助函数：of_platform_default_populate()/of_platform_populate()

```c
// drivers/of/platform.c
// 参数都是 NULL
int of_platform_default_populate(struct device_node *root,
				 const struct of_dev_auxdata *lookup,
				 struct device *parent)
{
	static const struct of_device_id match_table[] = {
		{ .compatible = "simple-bus", },
		{ .compatible = "simple-mfd", },
		{ .compatible = "isa", },
#ifdef CONFIG_ARM_AMBA
		{ .compatible = "arm,amba-bus", },
#endif /* CONFIG_ARM_AMBA */
		{} /* Empty terminated list */
	};

	return of_platform_populate(root, match_table, lookup, parent);
}
EXPORT_SYMBOL_GPL(of_platform_default_populate);

// drivers/of/platform.c
// 除了 matches，其他参数都是 NULL
int of_platform_populate(struct device_node *root,
			const struct of_device_id *matches,
			const struct of_dev_auxdata *lookup,
			struct device *parent)
{
	int rc = 0;

	// If the caller provided a root node, it uses that.
	// Otherwise, it finds the root of the entire device tree, /.
	// It also properly increments the reference count of the node.
	root = root ? of_node_get(root) : of_find_node_by_path("/");
	if (!root)
		return -EINVAL;

	pr_debug("%s()\n", __func__);
	pr_debug(" starting at: %pOF\n", root);

	device_links_supplier_sync_state_pause();
	// It iterates through every direct child of the root node.
	for_each_child_of_node_scoped(root, child) {
		// It creates a platform_device for the child node.

		// If the child node itself matches one of the matches
		// (i.e., it's a bus like "simple-bus"),
		// of_platform_bus_create will then recursively call itself
		// on all of that child's children.

		// The true argument enforces a strict rule: a node will
		// only be turned into a device if it has a
		// compatible property.
		rc = of_platform_bus_create(child, matches, lookup, parent, true);
		if (rc)
			break;
	}
	device_links_supplier_sync_state_resume();

	// After successfully creating devices for all its children,
	// it sets a flag on the root node. This marks it as "populated"
	// to prevent it from being processed again and to help with
	// device removal later.
	of_node_set_flag(root, OF_POPULATED_BUS);

	of_node_put(root);
	return rc;
}
EXPORT_SYMBOL_GPL(of_platform_populate);
```

##### 辅助函数：of_platform_bus_create()

```c
// drivers/of/platform.c
// lookup parent 是 NULL，strict 是 true
static int of_platform_bus_create(struct device_node *bus,
				  const struct of_device_id *matches,
				  const struct of_dev_auxdata *lookup,
				  struct device *parent, bool strict)
{
	const struct of_dev_auxdata *auxdata;
	struct platform_device *dev;
	const char *bus_id = NULL;
	void *platform_data = NULL;
	int rc = 0;

	/* Make sure it has a compatible property */
	if (strict && (!of_property_present(bus, "compatible"))) {
		pr_debug("%s() - skipping %pOF, no compatible prop\n",
			 __func__, bus);
		return 0;
	}

	/* Skip nodes for which we don't want to create devices */
	if (unlikely(of_match_node(of_skipped_node_table, bus))) {
		pr_debug("%s() - skipping %pOF node\n", __func__, bus);
		return 0;
	}

	if (of_node_check_flag(bus, OF_POPULATED_BUS)) {
		pr_debug("%s() - skipping %pOF, already populated\n",
			__func__, bus);
		return 0;
	}

	auxdata = of_dev_lookup(lookup, bus);
	if (auxdata) {
		bus_id = auxdata->name;
		platform_data = auxdata->platform_data;
	}

	if (of_device_is_compatible(bus, "arm,primecell")) {
		/*
		 * Don't return an error here to keep compatibility with older
		 * device tree files.
		 */
		of_amba_device_create(bus, bus_id, platform_data, parent);
		return 0;
	}

	dev = of_platform_device_create_pdata(bus, bus_id, platform_data, parent);
	// - device create 失败，返回 0
	// - device create 成功，bus 匹配 match_table 失败，返回 0
	// - device create 成功，bus 匹配 match_table 成功，
	//   继续给 bus 的 child 调用 of_platform_bus_create
	if (!dev || !of_match_node(matches, bus))
		return 0;

	for_each_child_of_node_scoped(bus, child) {
		pr_debug("   create child: %pOF\n", child);
		rc = of_platform_bus_create(child, matches, lookup, &dev->dev, strict);
		if (rc)
			break;
	}
	of_node_set_flag(bus, OF_POPULATED_BUS);
	return rc;
}
```

##### 辅助函数：of_platform_device_create_pdata()

```c
// drivers/of/platform.c

static struct platform_device *of_platform_device_create_pdata(
					struct device_node *np,
					const char *bus_id,
					void *platform_data,
					struct device *parent)
{
	struct platform_device *dev;

	pr_debug("create platform device: %pOF\n", np);

	if (!of_device_is_available(np) ||
	    of_node_test_and_set_flag(np, OF_POPULATED))
		return NULL;

	// 分配，初始化 platform device
	// platform_device 中含有 resource 数组, 它来自 device_node 的 reg, interrupts 属性;
	// platform_device.dev.of_node 指向 device_node, 可以通过它获得其他属性
	dev = of_device_alloc(np, bus_id, parent);
	if (!dev)
		goto err_clear_flag;

	dev->dev.coherent_dma_mask = DMA_BIT_MASK(32);
	if (!dev->dev.dma_mask)
		dev->dev.dma_mask = &dev->dev.coherent_dma_mask;
	dev->dev.bus = &platform_bus_type;
	dev->dev.platform_data = platform_data;
	of_msi_configure(&dev->dev, dev->dev.of_node);

	// 把 platform device 注册到内核中
	if (of_device_add(dev) != 0) {
		platform_device_put(dev);
		goto err_clear_flag;
	}

	return dev;

err_clear_flag:
	of_node_clear_flag(np, OF_POPULATED);
	return NULL;
}
```

##### 辅助函数：of_device_add()/device_add()

```c
// drivers/of/platform.c

int of_device_add(struct platform_device *ofdev)
{
	BUG_ON(ofdev->dev.of_node == NULL);

	/* name and id have to be set so that the platform bus doesn't get
	 * confused on matching */
	ofdev->name = dev_name(&ofdev->dev);
	ofdev->id = PLATFORM_DEVID_NONE;

	/*
	 * If this device has not binding numa node in devicetree, that is
	 * of_node_to_nid returns NUMA_NO_NODE. device_add will assume that this
	 * device is on the same node as the parent.
	 */
	set_dev_node(&ofdev->dev, of_node_to_nid(ofdev->dev.of_node));

	return device_add(&ofdev->dev);
}

// drivers/base/core.c

int device_add(struct device *dev)
{
	...
	// 把 device 放入全局链表
	error = bus_add_device(dev);
	if (error)
		goto BusError;
	...
	// 找到对应的 driver 调用 probe 函数
	bus_probe_device(dev);
	...
}
```

##### 辅助函数：bus_probe_device()/device_initial_probe()

```c
// drivers/base/bus.c

void bus_probe_device(struct device *dev)
{
	struct subsys_private *sp = bus_to_subsys(dev->bus);
	struct subsys_interface *sif;

	if (!sp)
		return;

	if (sp->drivers_autoprobe)
		device_initial_probe(dev);

	mutex_lock(&sp->mutex);
	list_for_each_entry(sif, &sp->interfaces, node)
		if (sif->add_dev)
			sif->add_dev(dev, sif);
	mutex_unlock(&sp->mutex);
	subsys_put(sp);
}

// drivers/base/dd.c

void device_initial_probe(struct device *dev)
{
	__device_attach(dev, true);
}
```

##### 辅助函数：__device_attach()

```c
// drivers/base/dd.c

static int __device_attach(struct device *dev, bool allow_async)
{
	int ret = 0;
	bool async = false;

	device_lock(dev);
	if (dev->p->dead) {
		goto out_unlock;
	} else if (dev->driver) {
		if (device_is_bound(dev)) {
			ret = 1;
			goto out_unlock;
		}
		ret = device_bind_driver(dev);
		if (ret == 0)
			ret = 1;
		else {
			device_set_driver(dev, NULL);
			ret = 0;
		}
	} else {
		struct device_attach_data data = {
			.dev = dev,
			.check_async = allow_async,
			.want_async = false,
		};

		if (dev->parent)
			pm_runtime_get_sync(dev->parent);

		// 对每个 driver 调用 __device_attach_driver
		ret = bus_for_each_drv(dev->bus, NULL, &data,
					__device_attach_driver);
		if (!ret && allow_async && data.have_async) {
			/*
			 * If we could not find appropriate driver
			 * synchronously and we are allowed to do
			 * async probes and there are drivers that
			 * want to probe asynchronously, we'll
			 * try them.
			 */
			dev_dbg(dev, "scheduling asynchronous probe\n");
			get_device(dev);
			async = true;
		} else {
			pm_request_idle(dev);
		}

		if (dev->parent)
			pm_runtime_put(dev->parent);
	}
out_unlock:
	device_unlock(dev);
	if (async)
		async_schedule_dev(__device_attach_async_helper, dev);
	return ret;
}
```

##### 辅助函数：__device_attach_driver()/driver_match_device()

```c
// drivers/base/dd.c

static int __device_attach_driver(struct device_driver *drv, void *_data)
{
	struct device_attach_data *data = _data;
	struct device *dev = data->dev;
	bool async_allowed;
	int ret;

	// 进行 driver device 匹配
	ret = driver_match_device(drv, dev);
	if (ret == 0) {
		/* no match */
		return 0;
	} else if (ret == -EPROBE_DEFER) {
		dev_dbg(dev, "Device match requests probe deferral\n");
		dev->can_match = true;
		driver_deferred_probe_add(dev);
		/*
		 * Device can't match with a driver right now, so don't attempt
		 * to match or bind with other drivers on the bus.
		 */
		return ret;
	} else if (ret < 0) {
		dev_dbg(dev, "Bus failed to match device: %d\n", ret);
		return ret;
	} /* ret > 0 means positive match */

	async_allowed = driver_allows_async_probing(drv);

	if (async_allowed)
		data->have_async = true;

	if (data->check_async && async_allowed != data->want_async)
		return 0;

	/*
	 * Ignore errors returned by ->probe so that the next driver can try
	 * its luck.
	 */
	// 调用 driver 的 probe
	ret = driver_probe_device(drv, dev);
	if (ret < 0)
		return ret;
	return ret == 0;
}

// drivers/base/base.h

static inline int driver_match_device(const struct device_driver *drv,
				      struct device *dev)
{
	// platform_bus_type 的 match 是 platform_match
	return drv->bus->match ? drv->bus->match(dev, drv) : 1;
}
```

## Platform Driver

一般驱动会有一个 init 函数和一个 `struct platform_driver` 变量。init 函数中调用 `platform_driver_register(&...driver)` 注册 `struct platform_driver` 变量。

### platform_driver_register()

如上面所说，在 platform driver 的 init 函数调用 platform_driver_register 注册自己之前，of_platform_default_populate_init() 已经把设备树里的每个 platform device 添加到 platform bus 上。

现在每个 platform driver 的 init 函数调用 platform_driver_register 注册自己时，都会对 platform bus 的每个 dev 调用 __driver_attach 进行匹配。如果匹配成功，调用 driver 的 probe 函数。

调用链：

```
platform_driver_register
    __platform_driver_register
        driver_register
            bus_add_driver    // 把 driver 注册进 platform bus 的全局链表
                driver_attach // 对 platform bus 的每个 dev 调用 __driver_attach
                    __driver_attach
                        driver_match_device(drv, dev) // 判断drv dev是否匹配
                            platform_match
                        driver_probe_device(drv, dev) // 如果匹配，调用 drv probe
```

```c
// include/linux/platform_device.h

#define platform_driver_register(drv) \
	__platform_driver_register(drv, THIS_MODULE)
```

#### 辅助函数：__platform_driver_register()

```c
// drivers/base/platform.c

int __platform_driver_register(struct platform_driver *drv,
				struct module *owner)
{
	drv->driver.owner = owner;
	drv->driver.bus = &platform_bus_type;

	return driver_register(&drv->driver);
}
```

#### 辅助函数：driver_register()

```c
// drivers/base/driver.c

int driver_register(struct device_driver *drv)
{
	int ret;
	struct device_driver *other;

	if (!bus_is_registered(drv->bus)) {
		pr_err("Driver '%s' was unable to register with bus_type '%s' because the bus was not initialized.\n",
			   drv->name, drv->bus->name);
		return -EINVAL;
	}

	if ((drv->bus->probe && drv->probe) ||
	    (drv->bus->remove && drv->remove) ||
	    (drv->bus->shutdown && drv->shutdown))
		pr_warn("Driver '%s' needs updating - please use "
			"bus_type methods\n", drv->name);

	other = driver_find(drv->name, drv->bus);
	if (other) {
		pr_err("Error: Driver '%s' is already registered, "
			"aborting...\n", drv->name);
		return -EBUSY;
	}

	// 把 driver 注册进 platform bus 的全局链表
	ret = bus_add_driver(drv);
	if (ret)
		return ret;
	ret = driver_add_groups(drv, drv->groups);
	if (ret) {
		bus_remove_driver(drv);
		return ret;
	}
	kobject_uevent(&drv->p->kobj, KOBJ_ADD);
	deferred_probe_extend_timeout();

	return ret;
}
```

#### 辅助函数：bus_add_driver()

```c
// drivers/base/bus.c

int bus_add_driver(struct device_driver *drv)
{
	struct subsys_private *sp = bus_to_subsys(drv->bus);
	struct driver_private *priv;
	int error = 0;

	if (!sp)
		return -EINVAL;

	/*
	 * Reference in sp is now incremented and will be dropped when
	 * the driver is removed from the bus
	 */
	pr_debug("bus: '%s': add driver %s\n", sp->bus->name, drv->name);

	priv = kzalloc(sizeof(*priv), GFP_KERNEL);
	if (!priv) {
		error = -ENOMEM;
		goto out_put_bus;
	}
	klist_init(&priv->klist_devices, NULL, NULL);
	priv->driver = drv;
	drv->p = priv;
	priv->kobj.kset = sp->drivers_kset;
	error = kobject_init_and_add(&priv->kobj, &driver_ktype, NULL,
				     "%s", drv->name);
	if (error)
		goto out_unregister;

	klist_add_tail(&priv->knode_bus, &sp->klist_drivers);
	if (sp->drivers_autoprobe) {
		error = driver_attach(drv);
		if (error)
			goto out_del_list;
	}
	error = module_add_driver(drv->owner, drv);
	if (error) {
		printk(KERN_ERR "%s: failed to create module links for %s\n",
			__func__, drv->name);
		goto out_detach;
	}

	error = driver_create_file(drv, &driver_attr_uevent);
	if (error) {
		printk(KERN_ERR "%s: uevent attr (%s) failed\n",
			__func__, drv->name);
	}
	error = driver_add_groups(drv, sp->bus->drv_groups);
	if (error) {
		/* How the hell do we get out of this pickle? Give up */
		printk(KERN_ERR "%s: driver_add_groups(%s) failed\n",
			__func__, drv->name);
	}

	if (!drv->suppress_bind_attrs) {
		error = add_bind_files(drv);
		if (error) {
			/* Ditto */
			printk(KERN_ERR "%s: add_bind_files(%s) failed\n",
				__func__, drv->name);
		}
	}

	return 0;

out_detach:
	driver_detach(drv);
out_del_list:
	klist_del(&priv->knode_bus);
out_unregister:
	kobject_put(&priv->kobj);
	/* drv->p is freed in driver_release()  */
	drv->p = NULL;
out_put_bus:
	subsys_put(sp);
	return error;
}
```

#### 辅助函数：driver_attach()

```c
// drivers/base/dd.c

int driver_attach(const struct device_driver *drv)
{
	/* The (void *) will be put back to const * in __driver_attach() */
	return bus_for_each_dev(drv->bus, NULL, (void *)drv, __driver_attach);
}
```

#### 辅助函数：__driver_attach()/driver_match_device()

```c
// drivers/base/dd.c

static int __driver_attach(struct device *dev, void *data)
{
	const struct device_driver *drv = data;
	bool async = false;
	int ret;

	/*
	 * Lock device and try to bind to it. We drop the error
	 * here and always return 0, because we need to keep trying
	 * to bind to devices and some drivers will return an error
	 * simply if it didn't support the device.
	 *
	 * driver_probe_device() will spit a warning if there
	 * is an error.
	 */

	ret = driver_match_device(drv, dev);
	if (ret == 0) {
		/* no match */
		return 0;
	} else if (ret == -EPROBE_DEFER) {
		dev_dbg(dev, "Device match requests probe deferral\n");
		dev->can_match = true;
		driver_deferred_probe_add(dev);
		/*
		 * Driver could not match with device, but may match with
		 * another device on the bus.
		 */
		return 0;
	} else if (ret < 0) {
		dev_dbg(dev, "Bus failed to match device: %d\n", ret);
		/*
		 * Driver could not match with device, but may match with
		 * another device on the bus.
		 */
		return 0;
	} /* ret > 0 means positive match */

	if (driver_allows_async_probing(drv)) {
		/*
		 * Instead of probing the device synchronously we will
		 * probe it asynchronously to allow for more parallelism.
		 *
		 * We only take the device lock here in order to guarantee
		 * that the dev->driver and async_driver fields are protected
		 */
		dev_dbg(dev, "probing driver %s asynchronously\n", drv->name);
		device_lock(dev);
		if (!dev->driver && !dev->p->async_driver) {
			get_device(dev);
			dev->p->async_driver = drv;
			async = true;
		}
		device_unlock(dev);
		if (async)
			async_schedule_dev(__driver_attach_async_helper, dev);
		return 0;
	}

	__device_driver_lock(dev, dev->parent);
	driver_probe_device(drv, dev);
	__device_driver_unlock(dev, dev->parent);

	return 0;
}

// drivers/base/base.h

static inline int driver_match_device(const struct device_driver *drv,
				      struct device *dev)
{
	return drv->bus->match ? drv->bus->match(dev, drv) : 1;
}
```

### platform_match()

```c
// drivers/base/platform.c

const struct bus_type platform_bus_type = {
	.name		= "platform",
	.dev_groups	= platform_dev_groups,
	.match		= platform_match,
	.uevent		= platform_uevent,
	.probe		= platform_probe,
	.remove		= platform_remove,
	.shutdown	= platform_shutdown,
	.dma_configure	= platform_dma_configure,
	.dma_cleanup	= platform_dma_cleanup,
	.pm		= &platform_dev_pm_ops,
};
EXPORT_SYMBOL_GPL(platform_bus_type);

// drivers/base/platform.c

static int platform_match(struct device *dev, const struct device_driver *drv)
{
	struct platform_device *pdev = to_platform_device(dev);
	struct platform_driver *pdrv = to_platform_driver(drv);

	/* When driver_override is set, only bind to the matching driver */
	if (pdev->driver_override)
		return !strcmp(pdev->driver_override, drv->name);

	/* Attempt an OF style match first */
	if (of_driver_match_device(dev, drv))
		return 1;

	/* Then try ACPI style match */
	if (acpi_driver_match_device(dev, drv))
		return 1;

	/* Then try to match against the id table */
	if (pdrv->id_table)
		return platform_match_id(pdrv->id_table, pdev) != NULL;

	/* fall-back to driver name match */
	return (strcmp(pdev->name, drv->name) == 0);
}
```

#### driver_override

比较 platform_device.driver_override 和 platform_driver.driver.name。

#### 设备树 match

比较 platform_device.dev.of_node 和 platform_driver.driver.of_match_table。

platform_device.dev.of_node 的类型为 `struct device_node *`，platform_driver.driver.of_match_table 类型为 `struct of_device_id *`。

```c
// include/linux/of.h

struct device_node {
	const char *name;
	phandle phandle;
	const char *full_name;
	struct fwnode_handle fwnode;

	struct	property *properties;
	struct	property *deadprops;	/* removed properties */
	struct	device_node *parent;
	struct	device_node *child;
	struct	device_node *sibling;
#if defined(CONFIG_OF_KOBJ)
	struct	kobject kobj;
#endif
	unsigned long _flags;
	void	*data;
};

// include/linux/mod_devicetable.h

struct of_device_id {
	char	name[32];
	char	type[32];
	char	compatible[128];
	const void *data;
};
```

具体比较在 `__of_device_is_compatible` 中发生。总结如下：

- 首先，如果 of_match_table 中含有 compatible 值，就跟 dev 的 compatile 属性比较，若一致则成功，否则返回失败；
- 其次，如果 of_match_table 中含有 type 值，就跟 dev 的 device_type 属性比较，若一致则成功，否则返回失败；
- 最后，如果 of_match_table 中含有 name 值，就跟 dev 的 name 属性比较，若一致则成功，否则返回失败。

而设备树中建议不再使用 devcie_type 和 name 属性，所以基本上只使用设备节点的 compatible 属性来寻找匹配的 platform_driver。

```c
// include/linux/of_device.h

static inline int of_driver_match_device(struct device *dev,
					 const struct device_driver *drv)
{
	return of_match_device(drv->of_match_table, dev) != NULL;
}

// drivers/of/device.c

const struct of_device_id *of_match_device(const struct of_device_id *matches,
					   const struct device *dev)
{
	if (!matches || !dev->of_node || dev->of_node_reused)
		return NULL;
	return of_match_node(matches, dev->of_node);
}

// drivers/of/base.c

const struct of_device_id *of_match_node(const struct of_device_id *matches,
					 const struct device_node *node)
{
	const struct of_device_id *match;
	unsigned long flags;

	raw_spin_lock_irqsave(&devtree_lock, flags);
	match = __of_match_node(matches, node);
	raw_spin_unlock_irqrestore(&devtree_lock, flags);
	return match;
}

// drivers/of/base.c

static
const struct of_device_id *__of_match_node(const struct of_device_id *matches,
					   const struct device_node *node)
{
	const struct of_device_id *best_match = NULL;
	int score, best_score = 0;

	if (!matches)
		return NULL;

	for (; matches->name[0] || matches->type[0] || matches->compatible[0]; matches++) {
		score = __of_device_is_compatible(node, matches->compatible,
						  matches->type, matches->name);
		if (score > best_score) {
			best_match = matches;
			best_score = score;
		}
	}

	return best_match;
}

// drivers/of/base.c

static int __of_device_is_compatible(const struct device_node *device,
				     const char *compat, const char *type, const char *name)
{
	const struct property *prop;
	const char *cp;
	int index = 0, score = 0;

	/* Compatible match has highest priority */
	if (compat && compat[0]) {
		prop = __of_find_property(device, "compatible", NULL);
		for (cp = of_prop_next_string(prop, NULL); cp;
		     cp = of_prop_next_string(prop, cp), index++) {
			if (of_compat_cmp(cp, compat, strlen(compat)) == 0) {
				score = INT_MAX/2 - (index << 2);
				break;
			}
		}
		if (!score)
			return 0;
	}

	/* Matching type is better than matching name */
	if (type && type[0]) {
		if (!__of_node_is_type(device, type))
			return 0;
		score += 2;
	}

	/* Matching name is a bit better than not */
	if (name && name[0]) {
		if (!of_node_name_eq(device, name))
			return 0;
		score++;
	}

	return score;
}
```

#### id_table

比较 platform_device.name 和 platform_driver.id_table[i].name。

`platform_driver.id_table` 的类型为 `struct platform_device_id *`，表示该 driver 支持若干个 device。`id_table` 中列出了各个 device 的 `name` `driver_data`，其中的 name 表示该 drv 支持的设备的名字，driver_data 是些提供给该 device 的私有数据。

```c
// include/linux/mod_devicetable.h

struct platform_device_id {
	char name[PLATFORM_NAME_SIZE];
	kernel_ulong_t driver_data;
};
```

```c
// drivers/base/platform.c

static const struct platform_device_id *platform_match_id(
			const struct platform_device_id *id,
			struct platform_device *pdev)
{
	while (id->name[0]) {
		if (strcmp(pdev->name, id->name) == 0) {
			pdev->id_entry = id;
			return id;
		}
		id++;
	}
	return NULL;
}
```

#### name

比较 platform_device.name 和 platform_driver.driver.name。

## 中断处理

### 中断处理的几个原则

我们可以自己设想一下，对 Linux 这种大型操作系统，如果我们来设计中断处理，应该怎么设计。

第一、中断不能嵌套。如果中断可以嵌套，那么中断 B 可以中断中断 A 的处理函数，中断 C 可以中断中断 B 的处理函数。这样到最后，栈会溢出。

为了防止这种情况发生，Linux 系统上中断无法嵌套：即当前中断 A 没处理完之前，不会响应另一个中断 B，即使它的优先级更高。

第二、中断处理越快越好。

- 我们已经说过中断不能嵌套，而线程调度依靠定时器中断。所以在中断处理时，不能进行线程调度，那么：
  - 在单芯片系统中，如果中断处理很慢，那应用程序在这段时间内就无法执行：系统显得很迟顿
  - 在 SMP 系统中，如果中断处理很慢，那么正在处理这个中断的 CPU 上的其他线程也无法执行
- 另外，如果中断处理很慢，中断处理的过程中也响应不了其他中断

所以 Linux 系统上中断处理越快越好。

第三、拆分。我们已经说过，中断处理越快越好，但是有时候中断处理就是需要很久，比如对于按键中断，我们需要等待几十毫秒消除机械抖动。这段时间内系统完全不能执行任何其他线程，也响应不了其他中断。

如果某个中断就是要做那么多事，我们可以把它拆分成两部分：紧急的、不紧急的。在 handler 函数里只做紧急的事，然后就重新开中断，让系统得以正常运行；那些不紧急的事，以后再处理，处理时是开中断的。这就是中断上半部和中断下半部。

### 驱动如何注册上半部处理函数

```c
// include/linux/interrupt.h

extern int __must_check
request_threaded_irq(unsigned int irq, irq_handler_t handler,
		     irq_handler_t thread_fn,
		     unsigned long flags, const char *name, void *dev);

/**
 * request_irq - Add a handler for an interrupt line
 * @irq:	The interrupt line to allocate
 * @handler:	Function to be called when the IRQ occurs.
 *		Primary handler for threaded interrupts
 *		If NULL, the default primary handler is installed
 * @flags:	Handling flags
 * @name:	Name of the device generating this interrupt
 * @dev:	A cookie passed to the handler function
 *
 * This call allocates an interrupt and establishes a handler; see
 * the documentation for request_threaded_irq() for details.
 */
static inline int __must_check
request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags,
	    const char *name, void *dev)
{
	return request_threaded_irq(irq, handler, NULL, flags | IRQF_COND_ONESHOT, name, dev);
}
```

### 中断相关 CONFIG

``` kconfig
### arch/Kconfig

config HAVE_IRQ_EXIT_ON_IRQ_STACK
	bool
	help
	  Architecture doesn't only execute the irq handler on the irq stack
	  but also irq_exit(). This way we can process softirqs on this irq
	  stack instead of switching to a new one when we call __do_softirq()
	  in the end of an hardirq.
	  This spares a stack switch and improves cache usage on softirq
	  processing.

config HAVE_SOFTIRQ_ON_OWN_STACK
	bool
	help
	  Architecture provides a function to run __do_softirq() on a
	  separate stack.

config SOFTIRQ_ON_OWN_STACK
	def_bool HAVE_SOFTIRQ_ON_OWN_STACK && !PREEMPT_RT

### kernel/irq

# Generic irq_domain hw <--> linux irq number translation
config IRQ_DOMAIN
	bool

# Support forced irq threading
config IRQ_FORCED_THREADING
       bool

config SPARSE_IRQ
	bool "Support sparse irq numbering" if MAY_HAVE_SPARSE_IRQ
	help

	  Sparse irq numbering is useful for distro kernels that want
	  to define a high CONFIG_NR_CPUS value but still want to have
	  low kernel memory footprint on smaller machines.

	  ( Sparse irqs can also be beneficial on NUMA boxes, as they spread
	    out the interrupt descriptors in a more NUMA-friendly way. )

	  If you don't know what to do here, say N.

# 开启以后，可以自由把 handle_arch_irq 设置成架构相关处理函数
config GENERIC_IRQ_MULTI_HANDLER
	bool
	help
	  Allow to specify the low level IRQ handler at run time.
```

## 下半部实现方式：软中断 softirq

### 谁触发、谁执行

Linux 的 softirq 机制是与 SMP 密不可分的。为此，整个 softirq 机制的设计与实现中自始自终都贯彻了一个思想：“谁触发，谁执行”（Who marks，Who runs），也即触发软中断的那个 CPU 负责执行它所触发的软中断，而且每个 CPU 都有它自己的软中断触发与控制机制。这个设计思想也使得 softirq 机制充分利用了 SMP 系统的性能和特点。

### 软中断种类

```c
// include/linux/interrupt.h

/* PLEASE, avoid to allocate new softirqs, if you need not _really_ high
   frequency threaded job scheduling. For almost all the purposes
   tasklets are more than enough. F.e. all serial device BHs et
   al. should be converted to tasklets, not to softirqs.
 */

enum
{
	HI_SOFTIRQ=0,
	TIMER_SOFTIRQ,
	NET_TX_SOFTIRQ,
	NET_RX_SOFTIRQ,
	BLOCK_SOFTIRQ,
	IRQ_POLL_SOFTIRQ,
	TASKLET_SOFTIRQ,
	SCHED_SOFTIRQ,
	HRTIMER_SOFTIRQ,
	RCU_SOFTIRQ,    /* Preferable RCU should always be the last softirq */

	NR_SOFTIRQS
};
```

### 记录软中断对应的处理函数

系统一共定义了 10 个软中断请求描述符。软中断向量 i（0 ≤ i ≤ 9）所对应的软中断请求描述符就是 `softirq_vec[i]`。

这个数组是个系统全局数组，即它被所有的 CPU 所共享。这里需要注意的一点是：每个 CPU 虽然都有它自己的触发和控制机制，并且只执行他自己所触发的软中断请求，但是各个 CPU 所执行的软中断服务例程却是相同的，也即都是执行 `softirq_vec` 数组中定义的软中断服务函数。

```c
// include/linux/interrupt.h

struct softirq_action
{
	void	(*action)(void);
};

// kernel/softirq.c

static struct softirq_action softirq_vec[NR_SOFTIRQS] __cacheline_aligned_in_smp;
```

### 记录哪些软中断被触发

要实现「谁触发，谁执行」的思想，就必须为每个 CPU 都定义它自己的触发和控制变量。

`irq_stat` 的类型是 `struct irq_cpustat_t`，`__softirq_pending` 记录哪些软中断被触发。

```c
// include/asm-generic/hardirq.h

typedef struct {
	unsigned int __softirq_pending;
#ifdef ARCH_WANTS_NMI_IRQSTAT
	unsigned int __nmi_count;
#endif
} ____cacheline_aligned irq_cpustat_t;

DECLARE_PER_CPU_ALIGNED(irq_cpustat_t, irq_stat);

// kernel/softirq.c

#ifndef __ARCH_IRQ_STAT
DEFINE_PER_CPU_ALIGNED(irq_cpustat_t, irq_stat);
EXPORT_PER_CPU_SYMBOL(irq_stat);
#endif
```

`local_softirq_pending` 返回 `irq_stat.__softirq_pending`，`set_softirq_pending` 和 `or_softirq_pending` 对 `irq_stat.__softirq_pending` 进行更改。

```c
// include/linux/interrupt.h

#ifndef local_softirq_pending // RISC-V 没有定义

#ifndef local_softirq_pending_ref
#define local_softirq_pending_ref irq_stat.__softirq_pending
#endif

#define local_softirq_pending()	(__this_cpu_read(local_softirq_pending_ref))
#define set_softirq_pending(x)	(__this_cpu_write(local_softirq_pending_ref, (x)))
#define or_softirq_pending(x)	(__this_cpu_or(local_softirq_pending_ref, (x)))

#endif /* local_softirq_pending */
```

### 如何设置软中断的处理函数和触发软中断

一般来说，驱动的编写者不会也不宜直接使用 softirq。基本上都是使用基于 softirq 的 tasklet。

```c
// include/linux/interrupt.h

// 设置某个软中断对应的服务函数
extern void open_softirq(int nr, void (*action)(void));
// 触发软中断
extern void raise_softirq(unsigned int nr);

// kernel/softirq.c

void open_softirq(int nr, void (*action)(void))
{
	softirq_vec[nr].action = action;
}

void raise_softirq(unsigned int nr)
{
	unsigned long flags;

	local_irq_save(flags);
	raise_softirq_irqoff(nr);
	local_irq_restore(flags);
}

void __raise_softirq_irqoff(unsigned int nr)
{
	lockdep_assert_irqs_disabled();
	trace_softirq_raise(nr);
	or_softirq_pending(1UL << nr); // 对 irq_stat.__softirq_pending 进行更改
}
```

### 软中断初始化函数 softirq_init()

`softirq_init` 在 `start_kernel` 中被调用，主要设置 `TASKLET_SOFTIRQ` `HI_SOFTIRQ` 这两类软中断的处理函数。

```c

// kernel/softirq.c

/*
 * Tasklets
 */
struct tasklet_head {
	struct tasklet_struct *head;
	struct tasklet_struct **tail;
};

static DEFINE_PER_CPU(struct tasklet_head, tasklet_vec);
static DEFINE_PER_CPU(struct tasklet_head, tasklet_hi_vec);

// kernel/softirq.c

void __init softirq_init(void)
{
	int cpu;

	for_each_possible_cpu(cpu) {
		per_cpu(tasklet_vec, cpu).tail =
			&per_cpu(tasklet_vec, cpu).head;
		per_cpu(tasklet_hi_vec, cpu).tail =
			&per_cpu(tasklet_hi_vec, cpu).head;
	}

	// 设置 TASKLET_SOFTIRQ 和 HI_SOFTIRQ 对应的处理函数
	open_softirq(TASKLET_SOFTIRQ, tasklet_action);
	open_softirq(HI_SOFTIRQ, tasklet_hi_action);
}
```

### 中断处理

`do_irq -> handle_riscv_irq -> irq_exit_rcu -> __irq_exit_rcu`

```c
// kernel/softirq.c

static inline void __irq_exit_rcu(void)
{
#ifndef __ARCH_IRQ_EXIT_IRQS_DISABLED
	local_irq_disable();
#else
	lockdep_assert_irqs_disabled();
#endif
	account_hardirq_exit(current);
	preempt_count_sub(HARDIRQ_OFFSET);
	if (!in_interrupt() && local_softirq_pending())
		invoke_softirq();

	if (IS_ENABLED(CONFIG_IRQ_FORCED_THREADING) && force_irqthreads() &&
	    local_timers_pending_force_th() && !(in_nmi() | in_hardirq()))
		wake_timersd();

	tick_irq_exit();
}
```

函数 `invoke_softirq()` 负责执行数组 `softirq_vec[i]` 中设置的软中断服务函数。每个 CPU 都是通过执行这个函数来执行软中断服务的。

由于同一个 CPU 上的软中断服务例程不允许嵌套，因此，在调用 `invoke_softirq()` 函数之前就用 `in_interrupt()` 检查当前 CPU 是否正处在中断服务中，如果是则不执行 `invoke_softirq()` 函数。

举个例子，假设 CPU0 正在执行 `invoke_softirq()` 函数，执行过程产生了一个高优先级的硬件中断，于是 CPU0 转去执行这个高优先级中断所对应的中断服务程序。

众所周知，所有的中断服务程序最后都要跳转到 `do_irq()` 函数并由它来依次执行中断服务队列中的 ISR，这里我们假定这个高优先级中断的 ISR 请求触发了一次软中断，`do_irq()` 函数在退出之前调用 `__irq_exit_rcu()` 函数来服务软中断请求。

但是在这一次进入 `__irq_exit_rcu()` 函数时，它马上发现 CPU0 此前已经处在中断服务状态中了，因此这一次 `invoke_softirq` 函数不执行。

于是，CPU0 结束这次高优先级的中断处理，回到最开始的 `invoke_softirq()` 函数继续执行（，并为高优先级中断的 ISR 所触发的软中断请求补上一次服务？？）。

#### local_softirq_pending()

上面已经讨论过。

#### invoke_softirq()

在 `CONFIG_PREEMPT_RT` 开启的情况下，`invoke_softirq` 还有另外一种只使用 `wakeup_softirqd` 的实现，这里不讨论。

首先，我们检查 `force_irqthreads() && __this_cpu_read(ksoftirqd)`。`force_irqthreads()` 表示 is the kernel configured to force all interrupt handling into threads。This is an option for improving real-time characteristics without a full PREEMPT_RT patch. `__this_cpu_read(ksoftirqd)` 表示 is the `ksoftirqd` thread for this CPU running or available。

只有当这两个条件都满足时，才调用 `wakeup_softirqd` 处理软中断。否则调用 `__do_softirq` 或者 `do_softirq_own_stack` 处理软中断。

```c
// kernel/softirq.c

static inline void invoke_softirq(void)
{
	if (!force_irqthreads() || !__this_cpu_read(ksoftirqd)) {
#ifdef CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK
		/*
		 * We can safely execute softirq on the current stack if
		 * it is the irq stack, because it should be near empty
		 * at this stage.
		 */
		// 目前已经
		__do_softirq();
#else
		/*
		 * Otherwise, irq_exit() is called on the task stack that can
		 * be potentially deep already. So call softirq in its own stack
		 * to prevent from any overrun.
		 */
		// 使用 softirq stack
		do_softirq_own_stack();
#endif
	} else {
		wakeup_softirqd();
	}
}

// arch/riscv/kernel/irq.c

#ifdef CONFIG_SOFTIRQ_ON_OWN_STACK
static void ___do_softirq(struct pt_regs *regs)
{
	__do_softirq();
}

void do_softirq_own_stack(void)
{
	if (on_thread_stack())
		call_on_irq_stack(NULL, ___do_softirq);
	// If the kernel is not on a thread stack,
	// it implies it's already on the IRQ stack (for example,
	// if this code is being reached from a nested interrupt context).
	// In this case, it's already on a safe stack, so there's no need to
	// switch, and it can call __do_softirq() directly.
	else
		__do_softirq();
}
#endif /* CONFIG_SOFTIRQ_ON_OWN_STACK */

```

如果 `CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK` 开启，表示 softirq 在 irq stack 上处理，irq stack 此时基本已经空了，可以安全执行。如果 `CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK` 没开启，那么所有中断处理都是在 task kernel stack 上进行的

#### __do_softirq()




## 下半部实现方式：tasklet




## PLIC 初始化

PLIC 驱动实现文件为 `drivers/irqchip/irq-sifive-plic.c`。本来这个驱动的初始化函数是用 `IRQCHIP_DECLARE` 注册，在 `of_irq_init` 里被调用的，但是 commit 8ec99b033147 (irqchip/sifive-plic: Convert PLIC driver into a platform driver, 2024-02-22) 把 PLIC driver 变成了 platform driver。

`builtin_platform_driver` 创建了一个 `plic_driver_init` 函数，并在其中调用 `platform_driver_register(&plic_driver)`。

当 `plic_driver_init` 被执行时，`platform_driver_register` 被调用。`plic_driver.of_match_table` 和 platform bus 上的所有 platform evice 进行比较。`plic_driver.of_match_table` 和每个 platform device 比较时，`of_match_table` 里所有 entry 会一个一个和 platform device 比较。

- 对每个 platform device（假设为 plic）

  - 对 driver 的第一个 of_match_table entry `sifive,plic-1.0.0`

    - 调用 __of_device_is_compatible 匹配 device 和 `sifive,plic-1.0.0`

      如果当前 device 是 plic，那么 __of_device_is_compatible 返回的 score 要大

  - 对 driver 的第二个 of_match_table entry `riscv,plic0`

    - 调用 __of_device_is_compatible 匹配 device 和 `riscv,plic0`

      如果当前 device 是 plic，那么 __of_device_is_compatible 返回的 score 小一点

  - 最后返回的 match 是 of_match_table 第一个 entry

`plic_driver` 匹配到 plic 节点以后，`plic_platform_probe` 被调用。

```c
// drivers/irqchip/irq-sifive-plic.c

static const struct of_device_id plic_match[] = {
	{ .compatible = "sifive,plic-1.0.0" },
	{ .compatible = "riscv,plic0" },
	{ .compatible = "andestech,nceplic100",
	  .data = (const void *)BIT(PLIC_QUIRK_EDGE_INTERRUPT) },
	{ .compatible = "thead,c900-plic",
	  .data = (const void *)BIT(PLIC_QUIRK_EDGE_INTERRUPT) },
	{}
};

static int plic_platform_probe(struct platform_device *pdev)
{
	return plic_probe(pdev->dev.fwnode);
}

static struct platform_driver plic_driver = {
	.driver = {
		.name		= "riscv-plic",
		.of_match_table	= plic_match,
		.suppress_bind_attrs = true,
		.acpi_match_table = ACPI_PTR(plic_acpi_match),
	},
	.probe = plic_platform_probe,
};
builtin_platform_driver(plic_driver);
```

### plic_probe()
