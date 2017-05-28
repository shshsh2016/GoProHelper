import os
import time

import NetworkManager as NM



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

def scan():
    """Display available WiFi access points
    """
    for device in NM.NetworkManager.GetDevices():
        if device.DeviceType == NM.NM_DEVICE_TYPE_WIFI:
            for ap in device.GetAccessPoints():
                print('{:15s}  {:3d}%'.format(ap.Ssid, ap.Strength))  # , ap.Frequency/1000))



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



def find_wifi_device():
    """Search for WiFi device
    """
    for device in NM.NetworkManager.GetDevices():
        if device.DeviceType == NM.NM_DEVICE_TYPE_WIFI:
            return device


def connect_wifi(ssid):
    """Connect to known WiFi access point having specified SSID
    """
    # Connection information
    conn = find_wifi_connection(ssid)

    # Device information
    device = find_wifi_device()

    # Connect
    obj_path = '/'
    NM.NetworkManager.ActivateConnection(conn, device, obj_path)

    # Done
    return device



def check_state(device, timeout=60):
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
                    print('ok: {}'.format(current_connection()))

                    return

            time.sleep(time_delta)
            if time.time() - time_0 > timeout:
                return

    except KeyboardInterrupt:
        return

