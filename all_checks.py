#!/usr/bin/env python3

import os
import shutil
import sys
import psutil  # Untuk memeriksa suhu CPU
import subprocess

def check_reboot():
    """Return True if the computer has a pending reboot."""
    return os.path.exists("/run/reboot-required")

def check_disk_full(disk, min_gb, min_percent):
    """Return True if there isn't enough disk space, False otherwise."""
    du = shutil.disk_usage(disk)
    percent_free = 100 * du.free / du.total
    gigabytes_free = du.free / 2**30
    return gigabytes_free < min_gb or percent_free < min_percent

def check_root_full():
    """Return True if the root partition is full, False otherwise."""
    return check_disk_full(disk="/", min_gb=2, min_percent=10)

def check_updates():
    """Return True if there are pending updates, False otherwise."""
    try:
        result = subprocess.run(['apt', 'list', '--upgradable'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        updates = result.stdout.decode('utf-8').strip().split('\n')[1:]
        return len(updates) > 0
    except FileNotFoundError:
        return False

def check_network():
    """Return True if the network is down, False otherwise."""
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return False
    except subprocess.CalledProcessError:
        return True

def check_cpu_temperature(threshold=75):
    """Return True if the CPU temperature exceeds the threshold, False otherwise."""
    if hasattr(psutil, 'sensors_temperatures'):
        temp = psutil.sensors_temperatures().get('coretemp', [])
        for sensor in temp:
            if sensor.current > threshold:
                return True
    else:
        print("CPU temperature monitoring is not supported on this system.")
    return False


def main():
    checks = [
        (check_reboot, "Pending Reboot"),
        (check_root_full, "Root partition full"),
        (check_updates, "Pending system updates"),
        (check_network, "Network is down"),
        (check_cpu_temperature, "CPU temperature is too high")
    ]
    everything_ok = True
    for check, msg in checks:
        if check():
            print(f"\033[91m{msg}\033[0m")  # Red text for issues
            everything_ok = False

    if not everything_ok:
        sys.exit(1)

    print("\033[92mEverything is OK.\033[0m")  # Green text for all good
    sys.exit(0)

if __name__ == "__main__":
    main()
