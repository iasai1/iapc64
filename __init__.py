from __future__ import absolute_import, print_function, unicode_literals
import base64
import inspect
import json
import pickle
import sys
from ableton.v3.control_surface.elements.button import ButtonElement
from ableton.v3.base import const, listens, task
from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import CONTROLLER_ID_KEY, HIDDEN, NOTES_CC, PORTS_KEY, SCRIPT, SYNC, controller_id, inport, outport
from ableton.v3.control_surface.components import DEFAULT_DRUM_TRANSLATION_CHANNEL
from ableton.v3.live import liveobj_valid
from .colors import Rgb
from .device import DeviceComponent
from .display import display_specification
from .elements import Elements
from .global_quantization import GlobalQuantizationComponent
from .mappings import create_mappings
from .mixer import MixerComponent
from .recording import FixedLengthRecordingMethod
from .render_to_clip import RenderToClipComponent
from .session import SessionComponent
from .settings import SettingsComponent
from .skin import Skin
from .transport import TransportComponent

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536,
                          product_ids=[83],
                          model_name=['APC64']), 
     
     PORTS_KEY: [
                 inport(props=[NOTES_CC, SCRIPT, HIDDEN]),
                 outport(props=[NOTES_CC, SCRIPT, HIDDEN]),
                 outport(props=[SYNC])]}


def create_instance(c_instance):
    return APC64(c_instance=c_instance)

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    num_tracks = 8
    num_scenes = 8
    include_returns = True
    include_master = True
    right_align_non_player_tracks = True
    include_auto_arming = True
    feedback_channels = [DEFAULT_DRUM_TRANSLATION_CHANNEL]
    playing_feedback_velocity = Rgb.GREEN.midi_value
    recording_feedback_velocity = Rgb.RED.midi_value
    identity_response_id_bytes = (71, 83, 0, 25)
    create_mappings_function = create_mappings
    recording_method_type = FixedLengthRecordingMethod
    component_map = {'Device':DeviceComponent, 
     'Global_Quantization':GlobalQuantizationComponent,  
     'Render_To_Clip':RenderToClipComponent, 
     'Session':SessionComponent, 
     'Transport':TransportComponent}
    display_specification = display_specification

class APC64(ControlSurface):

    def __init__(self, *a, **k):
        (super().__init__)(Specification, *a, **k)

    def disconnect(self):
        self.elements.track_type_element.send_value(0)
        super().disconnect()

    def setup(self):
        duplicate_button = self.find_button("Duplicate_Button")
        clear_button = self.find_button("Clear_Button")
        mixer = MixerComponent(duplicate_button, clear_button)
        self.component_map['Mixer'] = mixer
        super().setup()
        self._APC64__on_pad_mode_changed.subject = self.component_map['Pad_Modes']
        logShit(self._c_instance)

    
    def find_button(self, name: str):
        return next((obj for obj in self.controls if getattr(obj, 'name', None) == name), None)

    def drum_group_changed(self, drum_group):
        has_drum_group = liveobj_valid(drum_group)
        self.elements.track_type_element.send_value(bool(has_drum_group))
        if not has_drum_group:
            pass
        if self.component_map['Pad_Modes'].selected_mode == 'drum':
            self.component_map['Pad_Modes'].selected_mode = 'note'

    def _get_additional_dependencies(self):
        settings = SettingsComponent()
        self.component_map['Settings'] = settings
        return {'settings_component': const(settings)}

    @listens('selected_mode')
    def __on_pad_mode_changed(self, selected_mode):
        self.set_can_update_controlled_track(selected_mode == 'drum')
        if selected_mode in ('session', 'session_overview', 'drum'):
            self._tasks.add(task.run(self.refresh_state))
        self.set_can_auto_arm(selected_mode not in ('session', 'session_overview'))

def logShit(obj):
    try:
        # Collect serializable state
        state = {k: v for k, v in obj.__dict__.items() if is_serializable(v)}

        # Collect methods
        methods = {name: str(method) for name, method in inspect.getmembers(obj, predicate=inspect.ismethod)}

        # Prepare log message
        state_str = "State:\n" + "\n".join([f"{k}: {v}" for k, v in state.items()])
        methods_str = "Methods:\n" + "\n".join([f"{name}: {method}" for name, method in methods.items()])

        # Log the state and methods
        logMsg(state_str)
        logMsg(methods_str)
    except Exception as e:
        logMsg(f"Failed to log object state and methods: {e}")

def is_serializable(obj):
    try:
        str(obj)
        return True
    except:
        return False

global logMsg
def logMsg(msg):
    sys.stderr.write(msg)

global logStuff
def logStuff(myobj):
        def custom_encoder(obj):
            try:
                # Get all attributes of the object
                attributes = vars(obj)
                # Serialize each attribute individually
                serialized_attributes = {}
                for key, value in attributes.items():
                    try:
                        # Get an array of variables excluding callable attributes
                        variables = {var: getattr(obj, var) for var in dir(obj) if not callable(getattr(obj, var))}
                        # Convert the variables to a JSON serializable format
                        serialized_variables = {key: str(value) for key, value in variables.items()}
                        # Return the serialized variables
                        return json.dumps(serialized_variables, skipkeys=True)
                    except TypeError:
                        # Custom serialization for non-serializable types
                        serialized_value = str(value)
                    serialized_attributes[key] = serialized_value
                # Return the serialized attributes
                return json.dumps(serialized_attributes)
                
            except Exception as e:
                # Handle serialization errors here
                return str(obj)
        sys.stderr.write(json.dumps(myobj, default=custom_encoder, indent=4))