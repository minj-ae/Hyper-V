import subprocess, shutil, re


templete_file = "Z:\Hyper-V\test\Virtual Hard Disks\test.vhdx" #Template File Path
Hyper_V_path = "Z:\Hyper-V" #Hyper-V default Path


def listToString(str_list):
    result = ""
    for s in str_list:
        result += s + " "
    return result.strip()

def Getipv4(str):
    result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", str)
    if result:
        return result
    else:
        return False

def Getip(vmname):
    a = subprocess.check_output(f"powershell.exe Get-VMNetworkAdapter -VMName {vmname}")
    b = Getipv4(a)
    ipv4_b = listToString(b)
    return ipv4_b

def SetVMStatus(vmname, status): # 전원 설정
    if status == "on":
        subprocess.check_output(f"powershell.exe Start-VM -Name {vmname}")
        return True
    if status == "off":
        subprocess.check_output(f"powershell.exe Stop-VM -Name {vmname} -Force")
        return True
    if status == "restart":
        subprocess.check_output(f"powershell.exe Restart-VM -Name {vmname} -Force")
        return True
    if status != "on" or "off" or "restart":
        return False

def SetVMMemory(vmname, memory):
    subprocess.check_output(f"powershell.exe Set-VMMemory {vmname} -DynamicMemoryEnabled $False -StartupBytes {memory}GB") # 메모리 설정

def SetVMProcessor(vmname, core, weight):
    subprocess.check_output(f"powershell.exe Set-VMProcessor {vmname} -Count {core} -Reserve 0 -Maximum 100 -RelativeWeight {weight}") # CPU 설정

def SetVMResourceMetering(vmname, status):
    if status == "on":
        subprocess.check_output(f"powershell.exe Enable-VMResourceMetering -VMName {vmname}") # 리소스 분석 켜기
        return True
    elif status == "off":
        subprocess.check_output(f"powershell.exe Disable-VMResourceMetering -VMName {vmname}") # 리소스 분석 끄기
        return True
    else:
        return False
        
def ResizeDisk(path, size):
    subprocess.check_output(f"powershell.exe Resize-VHD -Path {path} -SizeBytes {size}GB") # 디스크 설정

def Create(vmname, core, memory, disk, switch, weight):
    shutil.copyfile(fr"{templete_file}", fr"{Hyper_V_path}\{vmname}.vhdx")
    print("Copy Completed")
    subprocess.check_output(fr"powershell.exe New-VM -Switch {switch} -VHDPath '{Hyper_V_path}\{vmname}.vhdx' -Generation 1 -Name '{vmname}' -Path '{Hyper_V_path}'")
    SetVMProcessor(core, weight, vmname)
    SetVMMemory(memory, vmname)
    subprocess.check_output(fr"powershell.exe Resize-VHD -Path '{Hyper_V_path}\{vmname}.vhdx' -SizeBytes {disk}GB")
    subprocess.check_output(fr'powershell.exe Set-VMNetworkAdapter -VMName {vmname} -MaximumBandwidth 20480000 -MinimumBandwidthAbsolute 10240000') # 대역폭 10~20Mbps 설정
    SetVMStatus("on", vmname) # 가상머신 켜기

def Remove(vmname):
    subprocess.check_output(f'powershell.exe Remove-VM "{vmname}" -Force')

def GetVMinfo(vmname, core, memory):
    global setipv4
    setipv4 = subprocess.check_output(fr"powershell.exe GET-VMNetworkAdapter -VMName {vmname}") #아이피 조회
    return {"vmname": vmname, "memory": memory, "core": core, "ipv4": Getipv4(setipv4)}

def GetVMcore(vmname):
    a = subprocess.check_output(f"powershell.exe Get-VMProcessor {vmname}")
    core_b = a.split()
    return core_b[9]
    
def MeasureVM(vmname):
    subprocess.check_output(f"powershell.exe Measure-VM -VMName {vmname}") # 리소스 조회
    
def GetVMMemory(vmname):
    a = subprocess.check_output(f"powershell.exe Get-VMMemory {vmname}")
    memory_b = a.split()
    return memory_b[13]

def GetVMProcessor(vmname):
    processors = subprocess.check_output(f"powershell.exe Get-VMProcessor -VMName {vmname}")
    return {"Processor": processors}
