# GameInterfaceForToys
This project provides an interface to allow games to integrate with bluetooth enabled Sex Toys, allowing real-time tactile feedback from events that occur in-game. 

This project also integrates with Chaster, allowing games to manipulate a user's chastity sentence in various ways. Best not die in the game!

## Supported Toys
- All toys supported by [Buttplug.io](https://iostindex.com/?filter0Availability=Available,DIY&filter1Connection=Digital)
- All Lovense toys.
- Kizuna Smart Controller
- Edge-o-Matic 3000
- XBox controllers
- All physical chastity devices utilizing a key (Via Chaster)
- All toys that XToys supports.

## Supported Games
- Skyrim - All versions (Best Supported)
- Fallout 4 (Mod dependent)
- Mount and Blade: Bannerlord (Very basic)
- Night of Revenge: (Good support with included plugin)

## How does it work?
Upon launching the GIFT executable, the script actively watches for changes to the specified log (Papyrus.0.log for Skyrim and Fallout). Upon seeing a change to the log, it reads the latest content, and checks for any lines that match any events. If, for instance, the player starts having sex, the script will trigger any configured toys to activate (Vibrators vibrating, etc).

# Setup and Installation
- Download and extract the latest release of GIFT.
- Launch GIFT. You should see a screen like such:
![image](https://user-images.githubusercontent.com/7561884/210279788-78f1d902-d728-43b0-8e2a-e35b0605c5e2.png)
- Click the Configuration button (Options may have changed since this guide was written):
![image](https://github.com/user-attachments/assets/af90dec8-68a8-4331-934a-4e84b729641f)

Configure the options to your liking, and then click "Save". The application will then reload with the new settings.

## General Configuration
- Click "Select Log File", and then choose the log file to be processed.
- Enter your character's name under "Character Name".
- If using Linux or Mac, uncheck "Is the OS Windows?".

## Toy Configuration
- Select the toys that you want this session to use. In the above example, I am using Lovense toys, and the DG-Lab Coyote.

### Lovense
If using the Lovense interface, you have several options to control your toys.
1) You can run the Lovense Connect app on your local PC, and use it to connect to the toys. If you do so, you will need the Bluetooth dongle that Lovense makes. If you're running the Lovense app locally, you should enter `127.0.0.1:20010` for the Lovense Host.
2) You can run the Lovense app on your phone, and connect to it. If you're doing this, log into the app, and connect your toys. Select your profile, and enable "Game Mode". The IP address and port of your phone will be listed; Enter this into the "Lovense Host" field in the configuration menu. Example: `192.168.0.168:20010`.

You can restrict the maximum strength of Lovense vibrations with the "Lovense Strength Max" field. 100 = full strength, 50 = half strength, etc.

This interface offers the best support for Lovense devices in particular.

### Buttplug.io
If using buttplug.io, set the "Buttplug.io Server Address" to the IP of the device running initface connect. If this is running on your local PC, leave this at the default.
Like Lovense, you can also restrict the maximum strength of Buttplug.io vibrations here. 100 = full strength, 50 = half strength, etc.

### XToys
If using the XToys interface, you must load this script, and connect your toys: https://xtoys.app/scripts/-N_a05xsR9ehhX1aD1VQ
The script will provide a webhook ID - Enter this into the "XToys Webhook ID" field in settings. GIFT will now utilize XToys.

This interface offers the best compatibility with toys, but has a bit higher latency than the other interfaces.

### Chaster
Currently, Chaster integration requires that you obtain developer access on chaster. Access is easy to obtain though, just follow the instructions on the developer page. Once you've obtained this, you will need to generate a token, and enter it into the "Chaster Dev Token" field. This will authorize GIFT to manipulate locks that you have access to.
There are several other options:
- Chaster Lock Name: The name of the lock that chaster should operate on. If there are more than one lock with the same name, the script will reject this - names must be unique.
- Chaster Defeat Minimum Time To Add: The minimum number of seconds that Chaster should add to your lock's duration if you're defeated in combat.
- Chaster Defeat Maximum Time To Add: The maximum number of seconds that Chaster should add to your lock's duration if you're defeated in combat.

You should setup a lock [similar to this](https://chaster.app/shared-locks/62db96527885780555ce80b3) for full functionality (Or join my lock, I don't mind!).


## Game Specific Steps
### Skyrim and Fallout
For all versions of Skyrim and Fallout, you will need to enable papyrus logging in order for Skyrim to generate a log that GIFT can integrate with. You can find instructions on how to do this [here](https://www.nexusmods.com/skyrim/articles/368).

GIFT contains a plugin and several scripts to enhance it's ability to integrate with Skyrim. Under the "games" folder of the download, install the files contained under "skyrim" or "fallout" using your mod manager of choice.

### Night of Revenge
There are two ways of interfacing with this game.
1) Install the included plugin, and make sure that the interface is set to use the log reader in the settings. This is the preferred method, and provides the best support.
2) Alternatively, change the interface to "Screen reader". This will only work if you are playing in 4k resolution, and has higher latency and less precision than the other approach.

If using the plugin, you should set the log path to `\NightofRevenge_Data\output_log.txt`.

If using the plugin, I recommend the following settings for event configuration:
- Enemy Orgasm: Configured to use your estim device.
- Trap Orgasm: Configured to use vibrators/other toys.
- First Penetration: Configured to use your estim device.
- Player Orgasm: Configured to use vibrators/other toys.
- Player Damage: Configured to use your estim device.
- Player Death: Configured to use your estim device.
- Ero Animation Start: Configured to use vibrators/other toys.
- Ero Animation End: Configured to use vibrators/other toys.
- Game Over Start: Configured to use vibrators/other toys.
- Game Over End: Configured to use vibrators/other toys.

The following are relevant if you're using @btg's Ero mod (Which I recommend for the best experience):
- Struggle HP Damage: Configured to use your estim device.
- Struggle Good Struggle: Configured to use your estim device.
- Struggle Bad Struggle: Configured to use your estim device.

# Running the project via Python
I've tried to make this as painless as possible.
- Clone the repository.
- Run `pip install -r requirements.txt`
- The project lazy-loads dependencies for each toy type. Some toys have more involved setup processes (Like the Kizuna). Install any missing dependencies that were not in requirements.txt.
- Run `python GameInterfaceForToys.py`. 

# Advanced Configuration
GIFT exposes a number of files in the "data" folder, which can be manipulated in order to change how the application functions. 

## Events
As of version 1.2.0, GIFT allows users to configure the application to watch for whatever log lines they want. Under the `data/events/games` folder, there are [yaml files](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) containing the triggers that GIFT will respond to. For example, in data/events/games/skyrim/sexlab.yaml, this is one entry:
```
- Sex Start:
    regex: .+SEXLAB - ActorAlias\[{GIFT_ACTOR_NAME}\] SetActor.+
    function: sex_start
    case_sensitive: False
```
The syntax is:
```
- Name of Event:
    regex: The pattern to match.
    function: The function to call in GIFT's ["SkyrimScriptInterface" class](https://github.com/MinLL/GameInterfaceForToys/blob/master/GameInterfaceForToys.py#L158).
    case_sensitive: True or False, if the regex should be case sensitive.
```
Whenever "The pattern to match." appears in the log, the specified function will be executed. Generic shock and vibrate functions are exposed for making custom events:

### Generic Shock Example
```
- Plug Shocks:
    regex: .+Your plug gives a painfull shock.+
    function: generic_random_shock
    params:
        min_duration: 1
        max_duration: 5
        min_strength: 50
        max_strength: 65
```

### Generic Vibrate Example
```
- Pump Plug Inflate:
    regex: .+You hear your .+ plug pump whirr and inflating.*
    function: generic_random_vibrate
    params:
        duration: 10
        strength: 40
```

In the above examples, we can specify a range of minimum and maximum duration and strength, or just specify the duration and strength directly. The file `data/events.yaml` controls which yaml files are applied by GIFT. If you create a new yaml file of triggers, make sure to edit this file to enable it.

# Changing Patterns
TBD: Better documentation here. Vibrator patterns are currently stored under `data/vibrators/pattern_dict.json`. E-stim patterns are listed under the `data/estim/pattern_dict.json` file, and the `data/estim/patterns/` folder.
