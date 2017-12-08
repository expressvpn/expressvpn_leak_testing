# What are Leaks

Defining what a leak is can be tricky. The simplest definition of a leak could be considered to be

> Any scenario where a user's PII (Personally Identifiable Information) is exposed to 3rd parties.

A VPN application has several responsibilities. Two of those responsibilities are protecting your
privacy and securing your internet connection.

One of the ways in which a VPN application achieves these goals is to capture all network traffic
leaving a device, encrypt it and send it via the VPN provider’s servers. The net result is that the
only network traffic leaving the device will be an encrypted stream of data, which effectively
anonymises and secures your data from third party eavesdroppers or attackers.

A leak could thus be defined as any traffic which leaves a device unencrypted when the VPN is
connected. However, it turns out that this definition isn’t sufficient.

## What does it mean to say a VPN is connected?

We never defined what it means for a VPN to be “connected”. Does being connected mean that the VPN
application has an open encrypted channel with a VPN server?

This is a rather loose definition because it doesn’t account for situations such as

* The VPN application losing touch with the server
* The network being temporarily disrupted

From a user’s viewpoint, they shouldn’t care what happened to the VPN server, the network or the VPN
application. They just want to know they are connected.

We choose to use the definition of connected as:

“From the moment the user turns the VPN on, until the moment where the user consciously chooses to
“turn the VPN off”

Our goal is to ensure you are protected during that period regardless of what happens to the app or
network inbetween.

 When testing our own application this is the standard we hold ourselves to.

## What if my private data goes over the VPN connection?

Just because data is encrypted and sent over the VPN tunnel doesn’t mean you are protected against
privacy violations. When you browse the internet you often send Personally Identifiable Information
(PII) to third parties and do so deliberately, e.g.

* When you log in to a social networking website
* When you access your banking website

This is perfectly normal and desirable.

However, what if your PII is leaving your device which you didn’t want to leave? There are cases
where this can happen if a VPN application doesn’t perform properly. For example,

* Your public IP address being exposed to third parties even when connected
* Your DNS requests going to a public DNS server but via the VPN

When searching for potential leaks, we use the following broad rule to decide how far to cast the
net.

“When the user is connected to the VPN, no PII is exposed unless the user actively chooses to expose
“it.”

It’s unreasonable to ever expect perfection here. For example, a user could install an application
which is deliberately designed to mine PII from their device. Worse still, such an application could
have root privileges, giving it almost unrestrained access to a user's device. Thus the user has
some responsibility on protecting their own privacy.

However, by holding ourselves to such a broad definition it helps us to search for leaks which a
large number of users may face and try to find ways to fix these or, at worst, educate users.

## What does all this mean in practice?

When the user is “connected”, as defined above, the standards we currently follow are:

* Don’t send traffic unencrypted off device
* Don’t make a user’s public IPs visible to third parties
* Don’t allow a user’s DNS requests to be seen by any DNS server other than our own
