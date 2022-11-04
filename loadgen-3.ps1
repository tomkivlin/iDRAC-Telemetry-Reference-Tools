Disconnect-VIServer *
Connect-VIServer -Server "10.51.128.59" -User "root" -Password $password
$vm = New-VM -name "loadgen" -DiskGB 200 -MemoryGB 512 -NumCpu 54 -NetworkName "VM Network"
$cd = New-CDDrive -VM $vm -IsoPath "[datastore1] ubuntu-20.04.4-live-server-amd64.iso"
Set-CDDrive -CD $cd -StartConnected $true
Start-VM -VM $vm
Disconnect-VIServer *