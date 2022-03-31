@echo off
echo This script needs admin rights!
echo Setting new boot options to enable test-signed drivers, remove these when driver is officialy signed
bcdedit /debug on
bcdedit /set testsigning on
