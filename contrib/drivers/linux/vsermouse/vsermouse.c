/*
     Virtual Serial Mouse Driver
     
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
#define CLASS_NAME "vsermouse"

MODULE_AUTHOR("Sascha Kopp <sascha.kopp@stud.h-da.de>");
MODULE_DESCRIPTION("Mouse (i386) emulator");
MODULE_LICENSE("GPL");

static int vsermouse_major = 0;

static struct class* vsermouse_class = NULL;
static struct device* vsermouse_device = NULL;

/* We register this device as a serial bus driver to be able to 
   feed the scancode to the keyboard driver which also handles the normal
   keyboard. We identify as an rs232 with the msc protocol which normally interfaces to the msc mouse driver.
   This should be made a module parameter, if vsermouse should be
   used in combination with other physical mouses as well. */

/*
 * This is called by serio_open when connecting to the keyboard driver.
 * We need no additional actions here and return success.
 */
static int serio_vsermouse_open(struct serio *port)
{
	return 0;
}

/*
 * This is called by serio_close when the keyboard driver disconnects.
 * We need no actions here.
 */
static void serio_vsermouse_close(struct serio *port)
{
}

static int vsermouse_open(struct inode *inode, struct file *file)
{
	//printk("vsermouse module has been opened\n");
	return 0;
}
  
static int vsermouse_release(struct inode *inode, struct file *file)
{
	//printk("vsermouse module has been closed\n");
	return 0;
}

/* serio should be kmalloce'ed, or serio_unregister_port will segfault :( */
static struct serio *vsermouse_port; 

static ssize_t vsermouse_write(struct file *file, const char *buf, size_t length, loff_t *ppos)
{
	int err;
	int retval = 0;
	unsigned char scancode = 0;
	//printk("vsermouse module write() called\n");
	//BUG_ON(vsermouse_port != NULL);

	err = access_ok(VERIFY_READ, buf, length);
	if (err == 0) return -EFAULT;

	for (retval = 0; retval < length; retval++) {
		get_user(scancode, (char*)buf++);
		//printk("SERIO_SYMBOL = %x\n", (unsigned int)scancode);

		#if LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 20)
			serio_interrupt(vsermouse_port, scancode, 0, NULL);
		#else
			serio_interrupt(vsermouse_port, scancode, 0      );
		#endif
	}
	return retval;
}


static struct file_operations vsermouse_fops = { 
	.owner	 = THIS_MODULE,
	.write	 = vsermouse_write, 
	.open	 = vsermouse_open, 
	.release = vsermouse_release
};

//static DEVICE_ATTR(fifo, S_IWUSR, NULL, vsermouse_fifo_write);
//static DEVICE_ATTR(reset, S_IWUSR, NULL, NULL);

static int __init vsermouse_init(void)
{
	//int retval = 0;
	
	vsermouse_major = register_chrdev(0, DEVICE_NAME, &vsermouse_fops);
	if(vsermouse_major < 0)
	{
		printk("vsermouse: can't get major\n");
		return(-EIO);
	}

	vsermouse_port = kmalloc(sizeof (struct serio), GFP_KERNEL);
	if (vsermouse_port == NULL) return -ENOMEM;

	/*
 	 * The port structure.
 	 * Important is the type. 
	 * It will make the msc mouse driver sermouse connect to this port
 	 * open and close must be valid function pointers. All other
 	 * entries can be set to arbitrary values. 
 	 *
 	 * sermouse.c use phys as following:
 	 * sprintf(sermouse->phys, "%s/input0", serio->phys)
 	 * Destination phys defined in the 'struct sermouse' as char[32].
 	 * So, our phys should be no longer then
 	 * 32 - strlen("/input0"), 
 	 * i.e no longer then 25, INCLUDE terminated 0.
 	 */
	memset(vsermouse_port, 0, sizeof(struct serio));
	vsermouse_port->open = serio_vsermouse_open;
	vsermouse_port->close = serio_vsermouse_close;
	strcpy(vsermouse_port->name , "MSC Mouse Emulator Port");
	strcpy(vsermouse_port->phys , "Mouse Emulator");
	vsermouse_port->id.type = SERIO_RS232;
	vsermouse_port->id.proto = SERIO_MSC;
	vsermouse_port->id.id    = SERIO_ANY;
	vsermouse_port->id.extra = SERIO_ANY;
	

	/* register this driver as a serial io port */
	serio_register_port(vsermouse_port);
	
	vsermouse_class = class_create(THIS_MODULE, CLASS_NAME);
	if (IS_ERR(vsermouse_class)) {
		printk("failed to register device class '%s'\n", CLASS_NAME);
		return(-EIO);
	}
	
	vsermouse_device = device_create(vsermouse_class, NULL, MKDEV(vsermouse_major, 0), NULL, CLASS_NAME);// "_" DEVICE_NAME);
	if (IS_ERR(vsermouse_device)) {
		printk("failed to create device '%s_%s'\n", CLASS_NAME, DEVICE_NAME);
		return(-EIO);
	}
	
	//retval = device_create_file(vsermouse_device, &dev_attr_fifo);
	//if (retval < 0) {
	//	printk("failed to create write /sys endpoint - continuing without\n");
	//}
	//retval = device_create_file(vsermouse_device, &dev_attr_reset);
	//if (retval < 0) {
	//	printk("failed to create reset /sys endpoint - continuing without\n");
	//}

	printk("vsermouse: loaded\n");
	
	return 0;
}

static void __exit vsermouse_exit(void)
{
	serio_unregister_port(vsermouse_port);
	//device_remove_file(vsermouse_device, &dev_attr_fifo);
	//device_remove_file(vsermouse_device, &dev_attr_reset);
	device_destroy(vsermouse_class, MKDEV(vsermouse_major, 0));
	class_unregister(vsermouse_class);
	class_destroy(vsermouse_class);
	unregister_chrdev(vsermouse_major, DEVICE_NAME);
	printk("vsermouse: unloaded\n");
}

module_init(vsermouse_init);
module_exit(vsermouse_exit);
