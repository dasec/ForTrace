/*
     Virtual Keyboard Driver
     
     based on:
     keyboard emulator project by Reznic Valery <valery_reznic@users.sourceforge.net>
 
     Copyright (C) 2015 Sascha Kopp <sascha.kopp@stud.h-da.de>
 
     This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
 
     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.
 
*/

#ifdef MODVERSIONS
	#include <linux/modversions.h>
#endif

#include <linux/version.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/serio.h>
#include <linux/input.h>
#include <linux/device.h>
//#include <linux/kfifo.h>

#include <linux/slab.h>

#include <asm/uaccess.h>
#define KERNEL_VERSION(a,b,c) (((a) << 16) + ((b) << 8) + (c))

#define DEVICE_NAME "io"
#define CLASS_NAME "vkbd"

MODULE_AUTHOR("Sascha Kopp <sascha.kopp@stud.h-da.de>");
MODULE_DESCRIPTION("Keyboard (i386) emulator");
MODULE_LICENSE("GPL");

static int vkbd_major = 0;

static struct class* vkbd_class = NULL;
static struct device* vkbd_device = NULL;

/* We register this device as a serial bus driver to be able to 
   feed the scancode to the keyboard driver which also handles the normal
   keyboard. We identify as an i8042 XL which normally interfaces to the AT
   keyboard driver. This should be made a module parameter, if vkbd should be
   used in combination with other physical keyboards as well. */

/*
 * This is called by serio_open when connecting to the keyboard driver.
 * We need no additional actions here and return success.
 */
static int serio_vkbd_open(struct serio *port)
{
	return 0;
}

/*
 * This is called by serio_close when the keyboard driver disconnects.
 * We need no actions here.
 */
static void serio_vkbd_close(struct serio *port)
{
}

static int vkbd_open(struct inode *inode, struct file *file)
{
	//printk("vkbd module has been opened\n");
	return 0;
}
  
static int vkbd_release(struct inode *inode, struct file *file)
{
	//printk("vkbd module has been closed\n");
	return 0;
}

/* serio should be kmalloce'ed, or serio_unregister_port will segfault :( */
static struct serio *vkbd_port; 

static ssize_t vkbd_write(struct file *file, const char *buf, size_t length, loff_t *ppos)
{
	int err;
	int retval = 0;
	unsigned char scancode = 0;
	//printk("vkbd module write() called\n");
	//BUG_ON(vkbd_port != NULL);

	err = access_ok(VERIFY_READ, buf, length);
	if (err == 0) return -EFAULT;

	for (retval = 0; retval < length; retval++) {
		get_user(scancode, (char*)buf++);
		//printk("SYMBOL = %x\n", (unsigned int)scancode);

		#if LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 20)
			serio_interrupt(vkbd_port, scancode, 0, NULL);
		#else
			serio_interrupt(vkbd_port, scancode, 0      );
		#endif
	}
	return retval;
}


static struct file_operations vkbd_fops = { 
	.owner	 = THIS_MODULE,
	.write	 = vkbd_write, 
	.open	 = vkbd_open, 
	.release = vkbd_release
};

//static DEVICE_ATTR(fifo, S_IWUSR, NULL, vkbd_fifo_write);
//static DEVICE_ATTR(reset, S_IWUSR, NULL, NULL);

static int __init vkbd_init(void)
{
	//int retval = 0;
	
	vkbd_major = register_chrdev(0, DEVICE_NAME, &vkbd_fops);
	if(vkbd_major < 0)
	{
		printk("vkbd: can't get major\n");
		return(-EIO);
	}

	vkbd_port = kmalloc(sizeof (struct serio), GFP_KERNEL);
	if (vkbd_port == NULL) return -ENOMEM;

	/*
 	 * The port structure.
 	 * Important is the type. 
	 * It will make the AT keyboard driver atkbd connect to this port
 	 * open and close must be valid function pointers. All other
 	 * entries can be set to arbitrary values. 
 	 *
 	 * atkbd.c use phys as following:
 	 * sprintf(atkbd->phys, "%s/input0", serio->phys)
 	 * Destination phys defined in the 'struct atkbd' as char[32].
 	 * So, our phys should be no longer then
 	 * 32 - strlen("/input0"), 
 	 * i.e no longer then 25, INCLUDE terminated 0.
 	 */
	memset(vkbd_port, 0, sizeof(struct serio));
	vkbd_port->open = serio_vkbd_open;
	vkbd_port->close = serio_vkbd_close;
	strcpy(vkbd_port->name , "Kbd Emulator Port");
	strcpy(vkbd_port->phys , "Keyboard Emulator");
	vkbd_port->id.type = SERIO_8042_XL;
	vkbd_port->id.proto = SERIO_ANY;
	vkbd_port->id.id    = SERIO_ANY;
	vkbd_port->id.extra = SERIO_ANY;

	/* register this driver as a serial io port */
	serio_register_port(vkbd_port);
	
	vkbd_class = class_create(THIS_MODULE, CLASS_NAME);
	if (IS_ERR(vkbd_class)) {
		printk("failed to register device class '%s'\n", CLASS_NAME);
		return(-EIO);
	}
	
	vkbd_device = device_create(vkbd_class, NULL, MKDEV(vkbd_major, 0), NULL, CLASS_NAME);// "_" DEVICE_NAME);
	if (IS_ERR(vkbd_device)) {
		printk("failed to create device '%s_%s'\n", CLASS_NAME, DEVICE_NAME);
		return(-EIO);
	}
	
	//retval = device_create_file(vkbd_device, &dev_attr_fifo);
	//if (retval < 0) {
	//	printk("failed to create write /sys endpoint - continuing without\n");
	//}
	//retval = device_create_file(vkbd_device, &dev_attr_reset);
	//if (retval < 0) {
	//	printk("failed to create reset /sys endpoint - continuing without\n");
	//}

	printk("vkbd: loaded\n");
	return 0;
}

static void __exit vkbd_exit(void)
{
	serio_unregister_port(vkbd_port);
	//device_remove_file(vkbd_device, &dev_attr_fifo);
	//device_remove_file(vkbd_device, &dev_attr_reset);
	device_destroy(vkbd_class, MKDEV(vkbd_major, 0));
	class_unregister(vkbd_class);
	class_destroy(vkbd_class);
	unregister_chrdev(vkbd_major, DEVICE_NAME);
	printk("vkbd: unloaded\n");
}

module_init(vkbd_init);
module_exit(vkbd_exit);
