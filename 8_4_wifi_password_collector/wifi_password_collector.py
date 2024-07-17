import subprocess
from collections import namedtuple
import re
import platform


class WifiPasswordCollector:
    def __init__(self, verbose=1):
        self.verbose = verbose
        self.Profile = namedtuple("Profile", ["ssid", "security", "key"])

    def get_profiles(self):
        system = platform.system().lower()
        if system == "windows":
            return self.get_windows_profiles()
        elif system == "darwin":
            return self.get_osx_profiles()
        elif system == "linux":
            return self.get_linux_profiles()
        else:
            print(f"Sistema operativo no soportado: {system}")
            return []

    def get_windows_profiles(self):
        profiles = []
        try:
            ssids = self._get_windows_saved_ssids()
            for ssid in ssids:
                try:
                    ssid_details = subprocess.check_output(f'netsh wlan show profile "{ssid}" key=clear',
                                                           shell=True).decode('utf-8', errors='ignore')
                    key = next((k.strip().strip(":").strip() for k in
                                re.findall(r"Contenido de la clave\s*:\s*(.*)", ssid_details)), "None")
                    security = next(
                        (c.strip().strip(":").strip() for c in re.findall(r"Autenticación\s*:\s*(.*)", ssid_details)),
                        "Unknown")
                    profile = self.Profile(ssid=ssid, security=security, key=key)
                    profiles.append(profile)
                    if self.verbose:
                        self._print_profile(profile)
                except subprocess.CalledProcessError:
                    print(f"No se pudo obtener información para el SSID: {ssid}")
        except Exception as e:
            print(f"Error al obtener perfiles de Windows: {e}")
        return profiles

    def _get_windows_saved_ssids(self):
        output = subprocess.check_output("netsh wlan show profiles", shell=True).decode('utf-8', errors='ignore')
        return [profile.strip().strip(":").strip() for profile in
                re.findall(r"Perfil de todos los usuarios\s*:\s*(.*)", output)]

    def get_osx_profiles(self):
        profiles = []
        try:
            ssid = self._get_real_ssid()
            if not ssid:
                print("No se pudo obtener el SSID.")
                return profiles

            security = self._get_security_info(ssid)
            key = self._get_wifi_password(ssid)

            profile = self.Profile(ssid=ssid, security=security, key=key)
            profiles.append(profile)

            if self.verbose:
                self._print_profile(profile)
        except Exception as e:
            print(f"Error al obtener perfiles de OSX: {e}")
        return profiles

    def _get_real_ssid(self):
        cmd = """
        WirelessPort=$(networksetup -listallhardwareports | awk '/Wi-Fi|AirPort/{getline; print $NF}')
        SSID=$(networksetup -getairportnetwork "$WirelessPort" | cut -d " " -f4-)
        echo "$SSID"
        """
        return subprocess.check_output(cmd, shell=True, text=True).strip()

    def _get_security_info(self, ssid):
        cmd = f"echo dbt77auz | sudo -S wdutil info"
        wifi_output = subprocess.check_output(cmd, shell=True, text=True)
        for line in wifi_output.split('\n'):
            if line.strip().startswith("Security"):
                return line.split(":")[1].strip()
        return "Desconocido"

    def _get_wifi_password(self, ssid):
        cmd = f"/usr/bin/security find-generic-password -D 'AirPort network password' -a '{ssid}' -w"
        return subprocess.check_output(cmd, shell=True, text=True).strip()

    def get_linux_profiles(self):
        profiles = []
        try:
            # Obtener SSIDs
            ssids_output = subprocess.check_output("nmcli -t -f NAME connection show", shell=True).decode('utf-8')
            ssids = ssids_output.strip().split('\n')

            for ssid in ssids:
                try:
                    # Obtener seguridad
                    security_output = subprocess.check_output(
                        f"nmcli -s -g 802-11-wireless-security.key-mgmt connection show '{ssid}'", shell=True).decode(
                        'utf-8').strip()
                    security = security_output if security_output else "Open"

                    # Obtener contraseña
                    key_output = subprocess.check_output(
                        f"nmcli -s -g 802-11-wireless-security.psk connection show '{ssid}'", shell=True).decode(
                        'utf-8').strip()
                    key = key_output if key_output else "No password"

                    profile = self.Profile(ssid=ssid, security=security, key=key)
                    profiles.append(profile)
                    if self.verbose:
                        self._print_profile(profile)
                except subprocess.CalledProcessError:
                    print(f"No se pudo obtener información para el SSID: {ssid}")
        except Exception as e:
            print(f"Error al obtener perfiles de Linux: {e}")
        return profiles

    def _print_profile(self, profile):
        print(f"SSID: {profile.ssid}")
        print(f"Seguridad: {profile.security}")
        print(f"Contraseña: {profile.key}")
        print("--------------------")


if __name__ == "__main__":
    collector = WifiPasswordCollector(verbose=1)
    profiles = collector.get_profiles()
    for profile in profiles:
        print(f"SSID: {profile.ssid}")
        print(f"Seguridad: {profile.security}")
        print(f"Contraseña: {profile.key}")
        print("--------------------")
