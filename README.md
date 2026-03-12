# Timberborn homeassistant

Connect homeassistant to the timberborn API.

## Installation

The easiest way to install the integration is using [hacs](https://hacs.xyz/docs/use)
Once you've installed hacs you can proceed here.
Go to `Hacs (in the sidebar) > ... > Custom repositories`. There add `https://github.com/agroqirax/timberborn-hass`, select the type `Integration` and press `Add`.
The integration is now installed.

It is also possible to download this repo as a zip file and copy `custom_components/timberborn` from this repo into `custom_components` in the config folder of your hass install.

Since you're probably not running hass on the same computer as timberborn you'll need to install the **Remote Api Access** mod that allows all computers on the same network to access the api:

- [Steam workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3682669754)
- [Mod.io](https://mod.io/g/timberborn/m/remote-api-access)
- [Github](https://github.com/agroqirax/remoteapiaccess/releases/latest)

## Configuration

You'll need to find the IP address of the computer running timberborn. This can usually be found in the devices internet settings. Look for **IPv4 Address** in the format `192.168.x.xxx`.
If you're running hass on the same computer you're running timberborn you can also use `localhost` or `127.0.0.1`.

Then go to `Settings > Devices & services > Add integration > Timberborn` and enter the base url of the timberborn API.

The base url should be in the format `http://host:Port`.
Host is the IP address of the computer running timberborn.
Port is the port number configured in timberborn, default is 8080

You may add multiple instances of timberborn.

## Usage

Adapters are binary sensors & levers are rgb lights that can be switched on/off as well as have their color set. The brightness setting currently doesn't do anything.
