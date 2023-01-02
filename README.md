# GameInterfaceForToys
This project provides an interface to allow games to integrate with bluetooth enabled Sex Toys, allowing real-time tactile feedback from events that occur in-game. 

This project also integrates with Chaster, allowing games to manipulate a user's chastity sentence in various ways. Best not die in the game!

## Supported Toys
- All toys supported by [Buttplug.io](https://iostindex.com/?filter0Availability=Available,DIY&filter1Connection=Digital)
- All Lovense toys.
- Kizuna Smart Controller
- Edge-o-Matic 3000
- XBox controllers
- DG-Lab E-Stim

## Supported Games
- Skyrim - All versions (Best Supported)
- Fallout 4

## How does it work?
Upon launching the GIFT executable, the script actively watches for changes to the specified log (Papyrus.0.log for Skyrim and Fallout). Upon seeing a change to the log, it reads the latest content, and checks for any lines that match any events. If, for instance, the player starts having sex, the script will trigger any configured toys to activate (Vibrators vibrating, etc).

# Setup and Installation
- Download and extract the latest release of GIFT.
- Launch GIFT. You should see a screen like such:
![image](https://user-images.githubusercontent.com/7561884/210279788-78f1d902-d728-43b0-8e2a-e35b0605c5e2.png)
- Click the Configuration button (Options may have changed since this guide was written):
![image](https://user-images.githubusercontent.com/7561884/210279863-cbcef641-abb8-4e3d-b258-a8f044d57fc4.png)

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

### Buttplug.io
If using buttplug.io, set the "Buttplug.io Server Address" to the IP of the device running initface connect. If this is running on your local PC, leave this at the default.
Like Lovense, you can also restrict the maximum strength of Buttplug.io vibrations here. 100 = full strength, 50 = half strength, etc.


### DG-Lab Coyote (E-Stim)
First, play responsibly! Never use E-Stim above the waist, and do not use if you have a pacemaker or other medical condition. By using this feature you take full responsibility for any injury or mishap resulting from the use of this software.

To enable the Coyote, select it under supported toys. Click "Save". The script will then scan, attempting to find a DG-Lab. If it finds one, it will then connect to it.
There are a few configuration options available:
- Coyote E-Stim UID: This should contain the UID of your device. Incase the app cannot automatically find this, you will need to enter it manually. You can find this by pairing your device, and examining its properties.
- Coyote E-Stim Multiplier: All events in gift are rated from 0-100 in intensity, where 0 is off, and 100 is full intensity. The maximum strength that GIFT allows the DG-Lab to output is 768. The default value for this multiplier is 7.68, meaning that at 100 intensity, the Coyote will be at full strength.
- Coyote E-Stim Default Channel: The channel that is used for the E-Stim session (Only one currently supported).
- Coyote Sex Multiplier: The multiplier by which the strength should be changed for sex scenes. By default, reduces the strength to 20%.
- Coyote Plug Multiplier: The multiplier by which the strength should be changed for plug events. By default, reduces the strength to 10%.
- Coyote On-Hit Multiplier: The multiplier by which the strength should be changed for on-hit events. By default, these are at full strength.


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
Generic Shock Example:
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

Generic Vibrate Example:
```
- Pump Plug Inflate:
    regex: .+You hear your .+ plug pump whirr and inflating.*
    function: generic_random_vibrate
    params:
        min_duration: 10
        max_duration: 20
        strength: 40
```

On both of the above, yo# GameInterfaceForToys
This project provides an interface to allow games to integrate with bluetooth enabled Sex Toys, allowing real-time tactile feedback from events that occur in-game. 

This project also integrates with Chaster, allowing games to manipulate a user's chastity sentence in various ways. Best not die in the game!

## Supported Toys
- All toys supported by [Buttplug.io](https://iostindex.com/?filter0Availability=Available,DIY&filter1Connection=Digital)
- All Lovense toys.
- Kizuna Smart Controller
- Edge-o-Matic 3000
- XBox controllers
- DG-Lab E-Stim

## Supported Games
- Skyrim - All versions (Best Supported)
- Fallout 4

## How does it work?
Upon launching the GIFT executable, the script actively watches for changes to the specified log (Papyrus.0.log for Skyrim and Fallout). Upon seeing a change to the log, it reads the latest content, and checks for any lines that match any events. If, for instance, the player starts having sex, the script will trigger any configured toys to activate (Vibrators vibrating, etc).

# Setup and Installation
- Download and extract the latest release of GIFT.
- Launch GIFT. You should see a screen like such:
![image](https://user-images.githubusercontent.com/7561884/210279788-78f1d902-d728-43b0-8e2a-e35b0605c5e2.png)
- Click the Configuration button (Options may have changed since this guide was written):
![image](https://user-images.githubusercontent.com/7561884/210279863-cbcef641-abb8-4e3d-b258-a8f044d57fc4.png)

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

### Buttplug.io
If using buttplug.io, set the "Buttplug.io Server Address" to the IP of the device running initface connect. If this is running on your local PC, leave this at the default.
Like Lovense, you can also restrict the maximum strength of Buttplug.io vibrations here. 100 = full strength, 50 = half strength, etc.


### DG-Lab Coyote (E-Stim)
First, play responsibly! Never use E-Stim above the waist, and do not use if you have a pacemaker or other medical condition. By using this feature you take full responsibility for any injury or mishap resulting from the use of this software.

To enable the Coyote, select it under supported toys. Click "Save". The script will then scan, attempting to find a DG-Lab. If it finds one, it will then connect to it.
There are a few configuration options available:
- Coyote E-Stim UID: This should contain the UID of your device. Incase the app cannot automatically find this, you will need to enter it manually. You can find this by pairing your device, and examining its properties.
- Coyote E-Stim Multiplier: All events in gift are rated from 0-100 in intensity, where 0 is off, and 100 is full intensity. The maximum strength that GIFT allows the DG-Lab to output is 768. The default value for this multiplier is 7.68, meaning that at 100 intensity, the Coyote will be at full strength.
- Coyote E-Stim Default Channel: The channel that is used for the E-Stim session (Only one currently supported).
- Coyote Sex Multiplier: The multiplier by which the strength should be changed for sex scenes. By default, reduces the strength to 20%.
- Coyote Plug Multiplier: The multiplier by which the strength should be changed for plug events. By default, reduces the strength to 10%.
- Coyote On-Hit Multiplier: The multiplier by which the strength should be changed for on-hit events. By default, these are at full strength.


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
