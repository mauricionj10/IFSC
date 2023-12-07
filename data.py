# DATA COLLECT PROGRAM
# Author: Mauricio Neves Junior
# Version: 1.0
# Date: 07/12/2023

# Libraries
import cpuinfo
import psutil
import wmi

# Function for read the CPU Temperature
def get_cpu_temperature():
    try:
        w = wmi.WMI()
        temperature_info = w.Win32_TemperatureProbe()

        for sensor in temperature_info:
            if 'CPU' in sensor.Name:
                temperature = sensor.CurrentReading
                print(f"Temperature: {temperature}")
                return temperature


    except Exception as e:
        print(f"Erro ao obter a temperatura da CPU: {e}")
        return None

# Function to get the CPU Info
def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return info

# Function to get the CPU Usage
def get_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    return usage
