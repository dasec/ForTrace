obj-m := vsermouse.o
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

MODULE = vsermouse.ko

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
	/sbin/rmmod vsermouse

clean:
	rm -f $(MODULE) $(obj-m) vsermouse.mod.[co] .vsermouse.* Module.symvers modules.order
	rm -rf .tmp_versions
