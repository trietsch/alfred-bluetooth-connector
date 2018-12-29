#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow

log = None
GITHUB_SLUG = 'trietsch/alfred-bluetooth-connector'


def main(wf):
    if wf.update_available:
        wf.add_item('Update available for Alfred Bluetooth Connector!',
                    autocomplete='workflow:update',
                    valid=False)
    else:
        import json
        import sys
        from subprocess import check_output, Popen, PIPE
        import re

        bluetooth_devices_pipe = Popen(
            ["/bin/bash", "-c", "/usr/libexec/PlistBuddy -c \"print :0:_items:0:device_title\" /dev/stdin <<< $(system_profiler SPBluetoothDataType -xml)"], stdout=PIPE)
        bluetooth_devices_raw, err = bluetooth_devices_pipe.communicate()

        # The following regex is quite complex, though that is due to the fact that the Dicts provided by PlistBuddy are inconsistent in order. Therefore, the two fields we're reading "device_addr" and "device_isconnected" occur twice, in both orders. Below, we decide which of the two contains data and which doesn't.
        # Feel free to try it out: https://regex101.com/r/GB5UKd/2
        bluetooth_devices = re.findall(
            r"(?s).*?(?:Dict\s?\{)\s*(.*?)\s?\=\s?(?:Dict).*?(?:(?:(?:device_isconnected)\s?\=\s?(?:attrib_((?:No|Yes))).*?(?:device_addr)\s?\=\s?((?:[0-9A-F]{2}[:-]){5}(?:[0-9A-F]{2})))|(?:(?:device_addr)\s?\=\s?((?:[0-9A-F]{2}[:-]){5}(?:[0-9A-F]{2})).*?(?:device_isconnected)\s?\=\s?(?:attrib_((?:No|Yes)))))", bluetooth_devices_raw)

        for device in bluetooth_devices:
            address = device[3] if len(device[2]) == 0 else device[2]
            connected = device[4] if len(device[1]) == 0 else device[1]
            connected_text = "[Connected]" if connected == "Yes" else "[Disconnected]"

            name = device[0] + " " + connected_text

            wf.add_item(
                type='file',
                title=name,
                subtitle=address,
                uid=address,
                arg=address,
                valid=True
            )

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow(update_settings={'github_slug': GITHUB_SLUG})
    log = wf.logger
    sys.exit(wf.run(main))
