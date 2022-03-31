obj-m := vkbd.o
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

MODULE = vkbd.ko

MODULE_DIR = $(DESTDIR)/lib/modules/$(MODULE_KERNEL_VERSION)/misc
DEV_DIR    = $(DESTDIR)/dev

default:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

install:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules_install
	depmod -a

insmod:
	/sbin/insmod ./$(MODULE)

rmmod:
	/sbin/rmmod vkbd

clean:
	rm -f $(MODULE) $(obj-m) vkbd.mod.[co] .vkbd.* Module.symvers modules.order
	rm -rf .tmp_versions
