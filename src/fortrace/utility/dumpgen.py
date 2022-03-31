"""
The functions found in this file use virsh commands (and possible others) to generate information dumps from the guest systems.
"""
import subprocess


def guest_dump(guestname, filepath, dump):
    if dump.lower() == "mem" or dump.lower() == "memory":
        subprocess.run(["virsh", "dump", guestname, filepath, "--memory-only"])
        print("Memory dump created for " + guestname + " at " + filepath)
    else:
        print(dump + " dump not implemented yet")
    # TODO extend function, maybe give options -> turn into all around dump function - choice of which dump in parameter?
