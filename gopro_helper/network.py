import os
import time

import NetworkManager as NM
import requests
import numpy as np

from .namespace import Struct


def get(url, json=True, timeout=5):
    """Handy helper to GET information from URL
    """
    try:
        resp = requests.get(url, timeout=timeout)

        if resp.status_code == 200:
            if json:
                return resp.json()
            else:
                return resp
        else:
            print(resp.reason)
            print(resp.status_code)

            return resp
            # raise requests.RequestException('GET exception: {}'.format(url))

    except requests.ConnectTimeout:
        return
    except OSError:
        return



def download(url, path_save=None):
    """Download file from URL
    """
    if not path_save:
        path_save = os.path.realpath(os.path.curdir)

    chunk_size = 1024*128
    resp = requests.get(url, stream=True)

    if resp.status_code != 200:
        print(resp.headers)
        print(resp.status_code)
        msg = 'Problem making request for: {}'.format(url)

        raise requests.RequestException(msg)

    # Open local file for writing
    f = os.path.join(path_save, os.path.basename(url))

    try:
        with open(f, 'wb') as fp:
            for chunk in resp.iter_content(chunk_size):
                fp.write(chunk)

    except KeyboardInterrupt:
        os.remove(f)
        raise

    # Done
    return f

#################################################


def display_connection_details():
    """Display details about current network connection
    """
    c = NM.const

    for conn in NM.NetworkManager.ActiveConnections:
        settings = conn.Connection.GetSettings()

        for s in list(settings.keys()):
            if 'data' in settings[s]:
                settings[s + '-data'] = settings[s].pop('data')

        secrets = conn.Connection.GetSecrets()
        for key in secrets:
            settings[key].update(secrets[key])

        devices = ""
        if conn.Devices:
            devices = " (on %s)" % ", ".join([x.Interface for x in conn.Devices])

        print("Active connection: %s%s" % (settings['connection']['id'], devices))
        size = max([max([len(y) for y in list(x.keys()) + ['']]) for x in settings.values()])
        format = "      %%-%ds %%s" % (size + 5)

        for key, val in sorted(settings.items()):
            print("   %s" % key)
            for name, value in val.items():
                if not name == 'psk':
                    print(format % (name, value))

        for dev in conn.Devices:
            print("Device: %s" % dev.Interface)
            print("   Type             %s" % c('device_type', dev.DeviceType))
            # print("   IPv4 address     %s" % socket.inet_ntoa(struct.pack('L', dev.Ip4Address)))
            if hasattr(dev, 'HwAddress'):
                print("   MAC address      %s" % dev.HwAddress)
            print("   IPv4 config")
            print("      Addresses")
            for addr in dev.Ip4Config.Addresses:
                print("         %s/%d -> %s" % tuple(addr))

            print("      Routes")
            for route in dev.Ip4Config.Routes:
                print("         %s/%d -> %s (%d)" % tuple(route))

            print("      Nameservers")
            for ns in dev.Ip4Config.Nameservers:
                print("         %s" % ns)


def current_connection():
    for conn in NM.NetworkManager.ActiveConnections:
        settings = conn.Connection.GetSettings()

        msg = settings['802-11-wireless']['ssid']
        return msg
        # 'connection': {'id': 'GP26528824 2', 'uuid': 'd94b1be3-6cfc-465e-bbd4-66e26c546ad5', 'type':
        # print(settings)


def scan(pretty=True):
    """Display available WiFi access points
    """
    found = {}

    for device in NM.NetworkManager.GetDevices():
        if device.DeviceType == NM.NM_DEVICE_TYPE_WIFI:
            for ap in device.GetAccessPoints():
                if ap.Ssid in found:
                    if ap.Strength > found[ap.Ssid]:
                        found[ap.Ssid] = ap.Strength
                else:
                    found[ap.Ssid] = ap.Strength

    names = np.asarray(list(found.keys()))

    ix = np.argsort([n.lower() for n in names])

    results = []
    for n in names[ix]:
        results.append([n, found[n]])

    if pretty:
        pretty_results = []
        for ssid, strength in results:
            pretty_results.append('{:15s}: {}'.format(ssid, strength))
        return pretty_results
    else:
        return results


def find_wifi_access_point(ssid):
    for device in NM.NetworkManager.GetDevices():
        if device.DeviceType == NM.NM_DEVICE_TYPE_WIFI:
            for ap in device.GetAccessPoints():
                if ap.Ssid == ssid:
                    return ap



def find_wifi_connection(ssid):
    """Search through NetworkManager known WiFi connections for specified SSID
    """
    type_wifi = '802-11-wireless'

    # List the saved network connections known to NetworkManager
    wifi_details = None
    for conn in NM.Settings.ListConnections():
        conn_settings = conn.GetSettings()
        try:
            wifi_details = conn_settings[type_wifi]

            if wifi_details['ssid'] == ssid:
                return conn

        except KeyError:
            # Keep searching...
            continue

    # Nothing found...
    return None


def find_wifi_device():
    """Search for WiFi device
    """
    found = []
    for device in NM.NetworkManager.GetDevices():
        if device.DeviceType == NM.NM_DEVICE_TYPE_WIFI:
            found.append(device)

    if len(found) > 1:
        raise ValueError('Found multiple devices...')

    if len(found) == 0:
        raise ValueError('Found no devices...')

    return found[0]


def connect_wifi(ssid, check=True):
    """Connect to known WiFi access point having specified SSID
    """
    # Connection information
    conn = find_wifi_connection(ssid)
    if not conn:
        raise ValueError('Connection not found (or not known?) {}'.format(ssid))

    # Device information
    device = find_wifi_device()

    # Connect
    obj_path = '/'
    NM.NetworkManager.ActivateConnection(conn, device, obj_path)

    if check:
        check_state(device, timeout=60)

    # Done



def check_state(device, timeout=60):
    """Continue querying network status and printing new values to console.
    Return when network is ready.
    """
    time_delta = 0.01
    state_last = -1

    time_0 = time.time()
    try:
        while True:
            state, reason = device.StateReason
            if state != state_last:
                state_last = state
                time_0 = time.time()

                state_str = NM.const('device_state', state)
                reason_str = NM.const('device_state_reason', reason)

                if reason:
                    msg = '{}  [{}]'.format(state_str, reason_str)
                else:
                    msg = '{}'.format(NM.const('device_state', state))

                print(msg)

                if state_str == 'activated':
                    print('connected: {}'.format(current_connection()))

                    return

            time.sleep(time_delta)
            if time.time() - time_0 > timeout:
                return

    except KeyboardInterrupt:
        return

#------------------------------------------------

if __name__ == '__main__':
    pass

