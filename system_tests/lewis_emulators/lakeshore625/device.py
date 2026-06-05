from collections import OrderedDict
from .states import DefaultState
from lewis.devices import StateMachineDevice

class FieldUnits(object):
    TESLA = object()

class SimulatedLakeshore625(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self.output_current = 0 # the current value that the output will ramp to at the present ramp rate - for SETI
        self.latest_current = 0 # actual measured output current # for RDGI
        self.current_ramp_rate = 0.01
        self.output_voltage = 0 # for RDGV
        self.output_compliance_voltage = 0 # for SETV
        self.remote_voltage = 0 # for RDGRV
        self.last_current = 0 # the last current setting when PSH was turned off

        self.trigger_output_current = 0
        self.external_program_mode = 0
        
        self.max_output_current = 60
        self.max_compliance_voltage_limit = 2
        self.max_ramp_rate = 1

        self.lock_state = 0
        self.lock_code = 000

        self.interface_mode = 0
        
        self.field_const = 0.1
        self.field_units = FieldUnits.TESLA
        self.field_output_reading = 0
        self.field_output_setting = 0
        
        self.quench_detection = True
        self.step_limit = 2
        
        self.ramp_segments = False
        self.ramp_segment_num = 1
        self.ramp_seg_current = 0
        self.ramp_seg_rate = 0.0001

        self.persistent_switch_enable = False
        self.persistent_switch_mode = False
        self.PSH_current = 10
        self.PSH_last_current = 0
        self.PSH_delay_time = 5
        self.persistent_mode_rate = False
        self.persistent_mode_ramp_rate = 0.1

        self.manufacturer = "LSCI"
        self.model = 625
        self.serial = 1234567
        self.firmware_version = 1.0

        self.power_up_settings = False
        self.factory_defaults = False
        self.trigger_event = False
        self.self_test = 0

        self.standard_event_status_register = 0
        self.standard_event_status_enable_register = 0
        self.status_byte_register = 0
        self.service_request_enable_register = 0
        self.master_summ_status_bit = 0



        self.operational_errors = 0
        self.PSH_errors = 0
        self.hardware_errors = 0
        self.operational_error_enable = 0
        self.PSH_error_enable = 0
        self.hardware_error_enable = 0
        ###
        self.operational_error_return = 0
        self.PSH_error_return = 0
        self.hardware_error_return = 0

        self.operational_status = 2
        self.operational_status_enable = 0
        self.operational_status_return = 0

        self.factory_defaults = False

    def reinitialize(self):
        self._initialize_data()
        
    def clear(self):
        self.status_byte_register = 0
        self.standard_event_status_register = 0 ## ?
    
    def set_ese(self, bit_weighting):
        self.standard_event_status_enable_register = bit_weighting

    def get_ese(self):
        return self.standard_event_status_enable_register
    
    def get_esr(self):
        return self.standard_event_status_register 
        
    def get_id(self):
        return {self.manufacturer, self.model, self.serial, self.firmware_version}
    
    def set_opc(self):
        self.standard_event_status_register = 1
        
    def get_opc(self):
        return 1
    
    def reset(self):
        self.power_up_settings = True # ?? come back to
    
    def set_sre(self, bit_weighting):
        self.service_request_enable_register = bit_weighting
    
    def get_sre(self):
        return self.service_request_enable_register
    
    def get_stb(self):
        status = (
            self.master_summ_status_bit * 64
        )
        return status
    
    def trigger(self):
        self.trigger_event = True
    
    def get_test(self):
        return self.self_test # ??
    
    def default(self):
        # sets all 'configuration values' (?) to factory defaults and resets the instrument - must be at zero amps to work
        if get_iout() == 0:
            self.factory_defaults = True

    def clr_err(self):
        # clears the operational and PSH errors
        self.operational_errors = 0
        self.PSH_errors = 0 # come back to ^
    
    def get_erst(self): # the integers returned represent the sum of the bit weighting of the error bits
        return {self.operational_errors, self.PSH_errors, self.hardware_errors}

    
    def set_erste(self, hardware_bit_weighting, operational_bit_weighting, PSH_bit_weighting):
        self.hardware_error_enable = hardware_bit_weighting
        self.operational_error_enable = operational_bit_weighting
        self.PSH_error_enable = PSH_bit_weighting
        # "to enable an error bit, send the command ERSTE with the sum of the bit weighting for each desired bit"

    def get_erste(self):
        return {self.hardware_error_enable, self.operational_error_enable, self.PSH_error_enable}
    
    def get_erstr(self):
        self.operational_error_return = self.operational_errors 
        self.PSH_error_return = self.PSH_errors
        self.hardware_error_return = self.hardware_errors
        clr_err() # register is cleared when it is read
        return {self.operational_error_return, self.PSH_error_return, self.hardware_error_return}
    
    def set_flds(self, units, constant):
        self.field_units = units
        self.field_const = constant
    
    def get_flds(self):
        return {self.field_units, self.field_const}
    
    def set_lim(self, current, voltage, rate):
        self.max_output_current = current
        self.max_compliance_voltage_limit = voltage
        self.max_ramp_rate = rate
    
    def get_lim(self):
        return {self.max_output_current, self.max_compliance_voltage_limit, self.max_ramp_rate}
    
    def set_lock(self, state, code):
        self.lock_state = state
        self.lock_code = code
    
    def get_lock(self):
        return {self.lock_state, self.lock_code}

    def set_mode(self, mode):
        self.interface_mode = mode

    def get_mode(self):
        return self.interface_mode
        
    def get_opst(self):
        return self.operational_status
    
    def set_opste(self, bit_weighting): # enable - come back to
        self.operational_status_enable = bit_weighting
    
    def get_opste(self): ## come back to
        return self.operational_status_enable
    
    def get_opstr(self): ## come back to
        self.operational_status_return = self.operational_status
        self.operational_status = 0 # register is cleared when read
        return self.operational_status_return
    
    def set_psh(self, mode):
        if self.persistent_switch_enable == 1 and self.last_current == self.latest_current:
            self.persistent_switch_mode = mode
        else:
            self.persistent_switch_mode = 0
    
    def get_psh(self):
        return self.persistent_switch_mode
    
    def get_pshis(self):
        return self.PSH_last_current
    
    def set_pshs(self, enable, current, delay):
        self.persistent_switch_enable = enable
        self.PSH_current = current
        self.PSH_delay_time = delay
        
    def get_pshs(self):
        return {self.persistent_switch_enable, self.PSH_current, self.PSH_delay_time}
    
    def set_qnch(self, enable, rate):
        self.quench_detection = enable
        self.step_limit = rate
    
    def get_qnch(self):
        return {self.quence_detection, self.step_limit}
    
    def set_rate(self, rate):
        self.current_ramp_rate = rate
    
    def get_rate(self):
        return self.current_ramp_rate
    
    def set_ratep(self, enable, rate):
        self.persistent_mode_rate = enable
        self.persistent_mode_ramp_rate = rate
    
    def get_ratep(self):
        return {self.persistent_mode_rate, self.persistent_mode_ramp_rate}
    
    def get_field(self):
        return self.field_output_reading
    
    def get_iout(self): ## read current
        return self.latest_current
    
    def get_vrem(self):
        return self.remote_voltage
    
    def get_vout(self): ## read voltage
        return self.output_voltage
    
    def set_rseg(self, enable):
        self.ramp_segments = enable
    
    def get_rseg(self):
        return self.ramp_segments
    
    def set_rsegs(self, segment, current, rate):
        if self.ramp_segments == 1:
            self.ramp_segment_num = segment
            self.ramp_seg_current = current
            self.ramp_seg_rate = rate
    
    def get_rsegs(self, ramp_segment_num):
        return {self.ramp_seg_current, self.ramp_seg_rate}
    
    def set_setf(self, field):
        self.field_output_setting = field
    
    def get_setf(self):
        return self.field_output_setting
    
    def set_seti(self, current): ## set output current to ramp to
        self.output_current = current
    
    def get_seti(self): ## get output current
        return self.output_current
    
    def set_setv(self, voltage): ## set output voltage
        self.output_compliance_voltage = voltage
    
    def get_setv(self): ## get output voltage
        return self.output_compliance_voltage
    
    def stop(self): ## stop output current
        self.output_current = 0
    
    def set_trig(self, value):
        self.trigger_output_current = value
    
    def get_trig(self):
        return self.trigger_output_current
    
    def set_xpgm(self, mode):
        self.external_program_mode = mode
    
    def get_xpgm(self):
        return self.external_program_mode
    
    
        
    
        
        
    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])
