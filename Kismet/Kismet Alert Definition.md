# Kismet - Alert Definition

Created by : Mr Dk.

2018 / 12 / 03 14:39

Nanjing, Jiangsu, China

---

### About

How does _kismet_ work as an _IDS_ ?

### Tools

The _IDS stuff_ of _kismet_ generally use these tools to generate attacks:

* _Lorcon_
  * a library for injecting 802.11 (WLAN) frames, capable of injecting via multiple driver frameworks, without the need to change the application code.
  * https://github.com/kismetwireless/lorcon
* _Aircrack_
  * _Aircrack-ng_ is a network software suite consisting of a detector, packet sniffer, WEP and WPA/WPA2-PSK cracker and analysis tool for 802.11 wireless LANs.
  * https://github.com/aircrack-ng/aircrack-ng
* _Karma_
  * A type of man-in-the-middle attack
* _Metaspolit_
  * The _Metasploit Project_ is a computer security project that provides information about security vulnerabilities and aids in penetration testing and IDS signature development.
  * https://github.com/rapid7/metasploit-framework
* _Reaver_

### Definition

Got information from _kismet RESTful API_ - `/alerts/definitions.json`

| Header              | Description                                                  | Attack                        | Tool        |
| ------------------- | ------------------------------------------------------------ | ----------------------------- | ----------- |
| `KISMET`            | Server events                                                | /                             | /           |
| `DHCPCLIENTID`      | A DHCP client sending a DHCP Discovery packet should provide a Client-ID tag (Tag 61) which matches the source MAC of the packet.  A client which fails to do so may be attempting to exhaust the DHCP pool with spoofed requests. | Spoofing / DoS                | /           |
| `NETSTUMBLER`       | Netstumbler (and similar older Windows tools) may generate unique beacons which can be used to __identify these tools__ in use.  These tools and the cards which generate these frames are uncommon. | /                             | Netstumbler |
| `NULLPROBERESP`     | A probe response with a SSID length of 0 can be used to crash the firmware in specific older Orinoco cards.  These cards are __unlikely to be in use__ in modern systems. | Crashing firmware             | /           |
| `LUCENTTEST`        | Specific Lucent Orinoco test tools generate identifiable frames, which can __indicate these tools__ are in use.  These tools and the cards which generate these frames are uncommon. | /                             | /           |
| `MSFBCOMSSID`       | Old versions of the Broadcom Windows drivers (and Linux NDIS drivers) are vulnerable to overflow exploits.  The Metasploit framework can attack these vulnerabilities.  These drivers are __unlikely to be found__ in modern systems, but seeing these malformed frames indicates an attempted attack is occurring. | Overflow                      | Metasploit  |
| `MSFDLINKRATE`      | Old versions of the D-Link Windows drivers are vulnerable to malformed rate fields.  The Metasploit framework can attack these vulnerabilities.  These drivers are __unlikely to be found__ in modern systems, but seeing these malformed frames indicates an attempted attack is occurring. | Malformed rate fields         | Metasploit  |
| `MSFNETGEARBEACON`  | Old versions of the Netgear windows drivers are vulnerable to malformed beacons.  The Metasploit framework can attack these vulnerabilities.  These drivers are __unlikely to be found__ in modern systems, but seeing these malformed frames indicates an attempted attack is occurring. | Malformed beacons             | Metasploit  |
| `LONGSSID`          | The Wi-Fi standard allows for 32 characters in a SSID. Historically, some drivers have had vulnerabilities related to invalid over-long SSID fields.  Seeing these frames indicates that significant corruption or an attempted attack is occurring. | Invalid over-long SSID        | /           |
| `DISCONCODEINVALID` | The 802.11 specification defines reason codes for __disconnect__ and __deauthentication__ events.  Historically, various drivers have been reported to improperly handle invalid reason codes.  An invalid reason code indicates an improperly behaving device or an attempted attack. | Invalid reason code           | /           |
| `DEAUTHCODEINVALID` | The 802.11 specification defines reason codes for __disconnect__ and __deauthentication__ events.  Historically, various drivers have been reported to improperly handle invalid reason codes.  An invalid reason code indicates an improperly behaving device or an attempted attack. | Invalid reason code           | /           |
| `WMMOVERFLOW`       | The Wi-Fi standard specifies 24 bytes for WMM IE tags.  Over-sized WMM fields may indicate an attempt to exploit bugs in Broadcom chipsets using the Broadpwn attack | Broadpwn                      | /           |
| `CHANCHANGE`        | An access point has changed channel.  This may occur on enterprise equipment or on personal equipment with automatic channel selection, but may also indicate a spoofed or 'evil twin' network. | Spoofing / 'Evil Twin'        | /           |
| `DHCPCONFLICT`      | A DHCP exchange was observed and a client was given an IP via DHCP, but is not using the assigned IP.  This may be a mis-configured client device, or may indicate client spoofing. | Spoofing                      | /           |
| `BCASTDISCON`       | A broadcast disconnect packet forces all clients on a network to disconnect.  While these may rarely occur in some environments, typically a broadcast disconnect indicates a denial of service attack or an attempt to attack the network encryption by forcing clients to reconnect. | DoS / Encryption attact       | /           |
| `AIRJACKSSID`       | Very old wireless tools used the SSID 'Airjack' while configuring card state.  It is very __unlikely to see__ these tools in operation in modern environments. | /                             | /           |
| `CRYPTODROP`        | A previously encrypted SSID has stopped advertising encryption.  This may rarely occur when a network is reconfigured to an open state, but more likely indicates some form of network spoofing or 'evil twin' attack. | Spoofing / 'Evil Twin'        | /           |
| `DHCPNAMECHANGE`    | The DHCP protocol allows clients to put the host name and DHCP client / vendor / operating system details in the DHCP Discovery packet.  These values should old change if the client has changed drastically (such as a dual-boot system with multiple operating systems).  Changing values can often indicate a client spoofing or MAC cloning attempt. | Spoofing / MAC cloning        | /           |
| `DHCPOSCHANGE`      | The DHCP protocol allows clients to put the host name and DHCP client / vendor / operating system details in the DHCP Discovery packet.  These values should old change if the client has changed drastically (such as a dual-boot system with multiple operating systems).  Changing values can often indicate a client spoofing or MAC cloning attempt. | Spoofing / MAC cloning        | /           |
| `ADHOCCONFLICT`     | The same SSID is being advertised as an access point and as an ad-hoc network.  This may indicate a misconfigured or misbehaving device, or could indicate an attempt at spoofing or an 'evil twin' attack. | Spoofing / 'Evil Twin'        | /           |
| `APSPOOF`           | Kismet may be given __a list of authorized MAC addresses for a SSID__.  If a beacon or probe response is seen from a MAC address not listed in the authorized list, this alert will be raised. | 'Evil Twin'                   | /           |
| `DOT11D`            | __Conflicting 802.11d (country code) data__ has been advertised __by the same SSID__.  It is unlikely this is a normal configuration change, and can indicate a spoofed or 'evil twin' network, or an attempt to perform a denial of service on clients by restricting their frequencies.  802.11d has been __phased out__ and is unlikely to be seen on modern devices, but it is still supported by many systems. | Spoofing / 'Evil Twin' / DoS  | /           |
| `BEACONRATE`        | The advertised beacon rate of a SSID has changed.  In an enterprise or multi-SSID environment this may indicate a normal configuration change, but can also indicate a spoofed or 'evil twin' network. | Spoofing / 'Evil Twin'        | /           |
| `ADVCRYPTCHANGE`    | A SSID has changed the advertised supported encryption standards.  This may be a normal change when reconfiguring an access point, but can also indicate a spoofed or 'evil twin' attack. | Spoofing / 'Evil Twin'        | /           |
| `MALFORMMGMT`       | __Malformed management frames__ may indicate errors in the capture source driver (such as not discarding corrupted packets), but can also be indicative of an attempted attack against drivers which may not properly handle malformed frames. | Attack against drivers        | /           |
| `WPSBRUTE`          | Excessive WPS events may indicate a malformed client, or an attack on the WPS system by a tool such as Reaver. | Attack on WPS system          | Reaver      |
| `KARMAOUI`          | Probe responses from MAC addresses with an OUI of 00:13:37 often indicate an Karma AP impersonation attack. | Karma AP impersonation attack | /           |
| `OVERPOWERED`       | Signal levels are abnormally high, when using an external amplifier this could indicate that the gain is too high.  Over-amplified signals may miss packets entirely. | /                             | /           |
| `NONCEDEGRADE`      | A WPA handshake with an empty NONCE was observed; this could indicate a WPA degradation attack such as the vanhoefm attack against BSD (https://github.com/vanhoefm/blackhat17-pocs/tree/master/openbsd) | WPA degradation attack        | vanhoefm    |
| `NONCEREUSE`        | A WPA handshake has attempted to re-use a previous nonce value; this may indicate an attack against the WPA keystream such as the vanhoefm KRACK attack (https://www.krackattacks.com/) | WPA keystream attack          | KRACK       |
| `WMMTSPEC`          | Too many WMMTSPEC options were seen in a probe response; this may be triggered by CVE-2017-11013 as described at https://pleasestopnamingvulnerabilities.com/ | /                             | /           |
| `RSNLOOP`           | Invalid RSN (802.11i) tags in beacon frames can be used to cause loops in some Atheros drivers, as described in CVE-2017-9714 and https://pleasestopnamingvulnerabilities.com/ | /                             | /           |
| `BCOM11KCHAN`       | Invalid channels in 802.11k neighbor report frames can be used to exploit certain Broadcom HardMAC implementations, typically used in mobile devices, as described in https://bugs.chromium.org/p/project-zero/issues/detail?id=1289 | /                             | /           |
| `BSSTIMESTAMP`      | An access point uses a high-precision timestamp in beacon frames to coordinate time-sensitive events. Vastly __out of sequence timestamps__ for __the same BSSID__ may indicate a spoofing or 'evil twin' style attack, however some APs may reset the timestamp regularly leading to a false positive. | Spoofing / 'Evil Twin'        | /           |
| `SOURCEERROR`       | A data source encountered an error.  Depending on the source configuration Kismet may automatically attempt to re-open the source. | /                             | /           |

---

### Summary

熟悉一下以上的攻击工具

重现可能出现的攻击

并查看 _kismet_ 是否能够检测出这些攻击

---

