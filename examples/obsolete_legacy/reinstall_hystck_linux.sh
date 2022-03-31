# this script will update the fortrace framework using a filesystem passthrough via 9p

# clear old files
cd ~
rm -r fortrace/
mkdir fortrace/

# mount shared folder (from host: /hostshare, to guest: /mnt/guestshare)
sudo mount -t 9p -o trans=virtio,version=9p2000.L /hostshare /mnt/guestshare

# get new files
cp -r /mnt/guestshare/* fortrace/
cd fortrace/

# update fortrace-installation
pip uninstall fortrace -y
pip install --user .