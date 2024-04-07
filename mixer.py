from __future__ import absolute_import, print_function, unicode_literals
import Live
from ableton.v3.control_surface.components import ChannelStripComponent
from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.components import SendIndexManager
from ableton.v3.control_surface.elements.button import ButtonElement
from ableton.v3.live.util import song, track_index

class TargetStripComponent(ChannelStripComponent):

    def __init__(self, *a, **k):
        (super().__init__)(*a, **k)
        self._send_controls = []
        self._send_index_manager = self.register_disconnectable(SendIndexManager(cycle_size=6))
        self.register_slot(self._send_index_manager, self._update_send_controls, 'send_index')

    def set_send_controls(self, controls):
        self._send_controls = controls or []
        self._update_send_controls()

    def cycle_send_index(self):
        self._send_index_manager.cycle_send_index(range_name='CH Strip')

    def _update_send_controls(self):
        if self._send_index_manager.send_index is None:
            self.send_controls.set_control_element(self._send_controls)
        else:
            self.send_controls.set_control_element([
             None] * self._send_index_manager.send_index + list(self._send_controls))
            self.update()

    @ChannelStripComponent.track_select_button.released_immediately
    def duplicate_or_delete_track(self, _):
        if self.parent._duplicate_button.is_pressed:
            song().duplicate_track(track_index(self._track))
            # change monitoring state on new track to avoid input volume jumps
            if self.song.view.selected_track.current_monitoring_state == 0:
                self.song.view.selected_track.current_monitoring_state = 2
        elif self._parent._clear_button.is_pressed:
            song().delete_track(track_index(self._track))
        
    @ChannelStripComponent.track_select_button.double_clicked
    def cycle_monitoring_or_fold_state(self, _):
        if self.song.view.selected_track.is_foldable == 1:
            new_value = (self.song.view.selected_track.fold_state + 1) % 2
            self.song.view.selected_track.fold_state = new_value
        elif self.song.view.selected_track.can_be_armed != 0: # filter out master and return tracks
            new_value = (self.song.view.selected_track.current_monitoring_state + 1) % 3
            self.song.view.selected_track.current_monitoring_state = new_value

class MixerComponent(MixerComponentBase):

    def __init__(self, duplicate_button, clear_button, *a, **k):
        self._duplicate_button = None
        self._clear_button = None
        self.set_dup_btn(duplicate_button)
        self.set_clear_btn(clear_button)
        super().__init__(*a, **k)

    def __getattr__(self, name):
        if name == 'set_target_track_send_controls':
            return self._target_strip.set_send_controls
        else:
            return super().__getattr__(name)
        
    def set_dup_btn(self, button):
        assert ((button == None) or (isinstance(button, ButtonElement) and button.is_momentary()))
        if self._duplicate_button != button:
            self._duplicate_button = button

    def set_clear_btn(self, button):
        assert ((button == None) or (isinstance(button, ButtonElement) and button.is_momentary()))
        if self._clear_button != button:
            self._clear_button = button
        
    def _create_channel_strip(self, is_master=False, is_target=False):
        if is_target:
            return TargetStripComponent(parent=self)
        else:
            return super()._create_channel_strip(is_master=is_master)
        

    
        
    
