
# IAPC64 - Improved APC64 Midi Remote Scripts for Ableton Live

IAPC64 is a collection of Abletons' session management improvements. These include:

- ability to duplicate tracks

- ability to delete tracks

- ability to fold/unfold track groups

- ability to change monitoring states of tracks

  

This repository only contains modified files. For proper use, you will need the original APC64 MIDI Remote Scripts

  

## Installation:

  

1. Locate MIDI Remote Scripts folder for your verison of Ableton live. Common locations include:

*Windows*: `C:\ProgramData\Ableton\Live x.x.x\Resources\MIDI Remote Scripts`

*Mac*: `/Applications/Ableton Live x.x.x.app/Contents/App-Resources/MIDI Remote Scripts`

  

2. Before proceeding, _make sure to backup the original APC64 scripts_ by copying the `APC64` folder to somewhere else on your computer.

  

3. Create a new folder inside the MIDI Remote Scripts folder, named `IAPC64`.

  

4. Copy all contents from `APC64` folder to `IAPC64` folder.

  

5. Replace `__init__.pyc` and `mixer.pyc` files in `IAPC64` folder with corresponding `*.pyc` files from this repository(located under `__pycache__` folder).

  

6. Boot up Ableton. In `Preferences > MIDI`, select `IAPC64` as control surface for your APC64 input/output.

  

## Usage

  

To `duplicate a track`, `hold _Duplicate_` button on the controller and `click a track` you want to copy on the track strip `*once*`.

To `delete a track`, `hold _Clear_` button on the controller and `click a track` you want to copy on the track strip `*once*`.

To `change montioring state` of a track, `double-click` the desired track on the track strip.

To `fold/unfold group` of tracks, `double-click` the desired track on the track strip.

  

## Tips and useful material for developers

  

- De-compiled Live 11 API: https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml

- Live object model: https://docs.cycling74.com/max5/refpages/m4l-ref/m4l_live_object_model.html

  

For logging you can use `sys.stderr.write()`. The messages will be outputted to the global `Log.txt` file, located at:
*Windows*: `%APPDATA%\Roaming\Ableton\Live x.x.x\Log.txt`
*Mac*: `~/Library/Preferences/Ableton/Live x.x.x/Log.txt`

  

You can import your own python dependencies into Ableton's runtime by navigating to resources folder. it is located in the same directory as `MIDI Remote Scripts`: `..Resources/Python/lib/site-packages`. This is useful if you wish to log Live's objects during runtime, as most of them are not JSON-serialazable