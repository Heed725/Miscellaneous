# Connect an HP LaserJet P4015 to a `192.168.100.x` Network

This guide explains how to connect an **HP LaserJet P4015** when the computer/router and printer currently use different IP address ranges.

## Current network information

| Device | Address | Status |
|---|---:|---|
| Router | `192.168.100.1` | Correct network |
| Printer | `192.168.2.105` | Wrong network range |
| Subnet mask | `255.255.255.0` | Standard local subnet |

The printer cannot normally communicate with the computer because `192.168.2.x` and `192.168.100.x` are different networks.

> **Important:** Do not assign `192.168.100.1` to the printer. That address belongs to the router.

## Recommended method: let the router assign an address

Use **DHCP** so that the router automatically gives the printer a valid and unused `192.168.100.x` address.

### Change the printer to DHCP

Using the control panel on the HP LaserJet P4015:

1. Press **Menu**.
2. Select **Configure Device**.
3. Select **I/O**.
4. Select **Embedded Jetdirect Menu**.
5. Select **TCP/IP**.
6. Select **IPv4 Settings**.
7. Select **Config Method**.
8. Change **Manual** to **DHCP**.
9. Restart the printer.

Make sure the printer's Ethernet cable is connected to the same router or network switch used by the computer.

### Find the printer's new IP address

After restarting the printer:

1. Press **Menu**.
2. Select **Information**.
3. Select **Print Configuration**.
4. Check the **IPv4 Address** on the printed page.

The new address should begin with:

```text
192.168.100.
```

Example:

```text
192.168.100.105
```

The last number may be different. Always use the exact address printed on the new configuration page.

## Add the printer in Windows

1. Open **Settings**.
2. Go to **Bluetooth & devices > Printers & scanners**.
3. Select **Add device**.
4. If Windows does not find it, select **Add manually**.
5. Select **Add a printer using an IP address or hostname**.
6. Enter the following:

   - **Device type:** `TCP/IP Device`
   - **Hostname or IP address:** the printer's new `192.168.100.x` address
   - **Port name:** allow Windows to fill it automatically

7. Leave **Query the printer and automatically select the driver to use** checked.
8. Select **Next**.
9. Choose **HP LaserJet P4015** when asked for a driver.

If the exact driver is unavailable, use **HP Universal Printing PCL 6**.

## Test the network connection

Open **Command Prompt** and run the following command, replacing the example address with the printer's new IP:

```cmd
ping 192.168.100.105
```

### Successful result

If you receive replies, the computer can reach the printer. Continue with the Windows printer installation.

### Request timed out

Check that:

- The printer's network cable is firmly connected.
- The printer is connected to the correct router or network switch.
- The computer is connected to the same network.
- The new printer address begins with `192.168.100.`.
- The router is not using guest-network or device-isolation settings.

## If Windows cannot detect the printer automatically

During the Windows installation:

1. Uncheck **Query the printer and automatically select the driver to use**.
2. Continue to the port settings.
3. Select **Standard TCP/IP Port**.
4. Use the following values:

   - **Protocol:** `RAW`
   - **Port number:** `9100`

5. Select the **HP LaserJet P4015** or **HP Universal Printing PCL 6** driver.
6. Finish the installation and print a test page.

## Manual address option

DHCP is recommended. If a fixed address is required, first confirm that the chosen address is unused or reserve it in the router. Example settings are:

```text
IP address:      192.168.100.105
Subnet mask:     255.255.255.0
Default gateway: 192.168.100.1
```

Do not use the example IP address until you have confirmed that another device is not already using it.

## Official support

- HP LaserJet P4010/P4510 connectivity guide: https://support.hp.com/ie-en/document/c01449158
- HP LaserJet P4015 setup and user guides: https://support.hp.com/us-en/product/setup-user-guides/hp-laser-p4015-series/3558793
