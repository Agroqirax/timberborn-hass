# Timberborn Home Assistant

Connect Home Assistant to the Timberborn API.
This integration exposes Timberborn automation blocks (adapters and levers) to Home Assistant so they can be used in automations.

## Installation

The easiest way to install the integration is using [HACS](https://hacs.xyz/docs/use).

After installing HACS, go to  
`HACS (in the sidebar) > ... > Custom repositories`.

Add:

```
https://github.com/agroqirax/timberborn-hass
```

Select the type **Integration** and press **Add**.

Close the popup, search for **Timberborn**, select it, and press **Download**.  
The integration is now installed.

Alternatively, download this repository as a zip file and copy  
`custom_components/timberborn` from this repo into the `custom_components` folder in your Home Assistant config directory.

Since Home Assistant is usually not running on the same computer as Timberborn, you'll need to install the **Remote Api Access** mod. This mod allows other computers on the same network to access the API.

- [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3682669754)
- [Mod.io](https://mod.io/g/timberborn/m/remote-api-access)
- [GitHub](https://github.com/agroqirax/remoteapiaccess/releases/latest)

## Configuration

### Automatically

Go to:

```
Settings > Devices & Services
```

Hass should automatically discover timberborn.
Just click add, name it and press submit.

For this you need timberborn-hass version 1.1.0 and Remote Api Access version 1.0.12.6.

### Manually

Find the IP address of the computer running Timberborn.  
This can usually be found in the device's network settings.

Look for **IPv4 Address** in the format:

```
192.168.x.xxx
```

If Home Assistant is running on the same computer as Timberborn, you can also use `localhost` or `127.0.0.1`.

Then go to:

```
Settings > Devices & Services > Add Integration > Timberborn
```

Enter the base URL of the Timberborn API.

The base URL should be in the format:

```
http://host:port
```

Example:

```
http://192.168.1.42:8080
```

- **Host** = IP address of the computer running Timberborn
- **Port** = Port configured in Timberborn (default: `8080`)

Multiple Timberborn instances can be added.

## Usage

Adapters appear as **binary sensors**.

Levers appear as **RGB lights** that can be turned on/off and have their color set.  
The brightness setting currently has no effect.

## Webhooks

This integration only uses the API for polling.  
To receive instant updates you can create a webhook automation like this:

```yaml
alias: Timberborn webhook
description: Notify user when adapter state changes
triggers:
  - trigger: webhook
    allowed_methods:
      - GET
      - POST
      - PUT
    local_only: false
    webhook_id: timberborn
conditions: []
actions:
  - action: notify.notify
    metadata: {}
    data:
      message: "{{trigger.query.name}} turned {{trigger.query.state}}"
mode: single
```

Then set the adapter webhook URL to something like:

```
http://homeassistant.local:8123/api/webhook/timberborn?name={name}&state=on
```

For the **off** URL use:

```
&state=off
```

`{name}` is replaced by the game with the adapter name before the request is sent.

Make sure to enable **"Call when switched on"** and **"Call when switched off"**, otherwise the webhook will not be triggered.
