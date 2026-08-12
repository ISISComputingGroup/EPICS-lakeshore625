from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class FieldUnits(object):
    TESLA = object()

class SimulatedLakeshore625(StateMachineDevice):

    def _initialize_data(self) -> None:
        """
        Initialize all of the device's attributes.
        """
        self.output_current = 0
        self.latest_current = 0
        self.current_ramp_rate = 0.01
        self.output_voltage = 0
        self.output_compliance_voltage = 0
        self.remote_voltage = 0
        self.last_current = 0

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
        self.ramp_seg_one_current = 0
        self.ramp_seg_one_rate = 0.0001
        self.ramp_seg_two_current = 1.0000
        self.ramp_seg_two_rate = 20.000
        self.ramp_seg_three_current = 10.0000
        self.ramp_seg_three_rate = 35.000
        self.ramp_seg_four_current = 30.100
        self.ramp_seg_four_rate = 45.100
        self.ramp_seg_five_current = 60.1000
        self.ramp_seg_five_rate = 99.999

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
        self.self_test = ""

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
        

    def reinitialize(self) -> None:
        self._initialize_data()
        
    def clear(self) -> None:
        self.status_byte_register = 0
        self.standard_event_status_register = 0
    
    def set_ese(self, bit_weighting: int) -> None:
        self.standard_event_status_enable_register = bit_weighting

    def get_ese(self) -> int:
        return self.standard_event_status_enable_register
    
    def get_esr(self) -> int:
        return self.standard_event_status_register 
        
    def get_id(self) -> set:
        return {self.manufacturer, self.model, self.serial, self.firmware_version}
    
    def set_opc(self) -> None:
        self.standard_event_status_register = 1
        
    def get_opc(self) -> int:
        return 1
    
    def reset(self) -> None:
        self.power_up_settings = True
    
    def set_sre(self, bit_weighting: int) -> None:
        self.service_request_enable_register = bit_weighting
    
    def get_sre(self) -> int:
        return self.service_request_enable_register
    
    def get_stb(self) -> int:
        status = (
            self.master_summ_status_bit * 64
        )
        return status
    
    def trigger(self) -> None:
        self.trigger_event = True
    
    def get_test(self) -> str:
        return self.self_test 
    
    def default(self) -> None:
        # sets all 'configuration values' to factory defaults and resets the instrument 
        # must be at zero amps to work
        if self.get_iout() == 0:
            self.factory_defaults = True

    def clr_err(self) -> None:
        # clears the operational and PSH errors
        self.operational_errors = 0
        self.PSH_errors = 0
    
    def get_erst(self) -> set[int]:
        return {self.operational_errors, self.PSH_errors, self.hardware_errors}

    
    def set_erste(self, hardware_bit_weighting: int, operational_bit_weighting: int, 
                  psh_bit_weighting: int) -> None:
        self.hardware_error_enable = hardware_bit_weighting
        self.operational_error_enable = operational_bit_weighting
        self.PSH_error_enable = psh_bit_weighting

    def get_erste(self) -> set[int]:
        return {self.hardware_error_enable, self.operational_error_enable, self.PSH_error_enable}
    
    def get_erstr(self) -> set[int]:
        self.operational_error_return = self.operational_errors 
        self.PSH_error_return = self.PSH_errors
        self.hardware_error_return = self.hardware_errors
        self.clr_err() # register is cleared when it is read
        return {self.operational_error_return, self.PSH_error_return, self.hardware_error_return}
    
    def set_flds(self, units: FieldUnits, constant: float) -> None:
        self.field_units = units
        self.field_const = constant
    
    def get_flds(self) -> set:
        return {self.field_units, self.field_const}
    
    def set_lim(self, current: float, voltage: float, rate: float) -> None:
        self.max_output_current = current
        self.max_compliance_voltage_limit = voltage
        self.max_ramp_rate = rate
    
    def get_lim(self) -> set[int | float]:
        return {self.max_output_current, self.max_compliance_voltage_limit, self.max_ramp_rate}
    
    def set_lock(self, state: int, code: int) -> None:
        self.lock_state = state
        self.lock_code = code
    
    def get_lock(self) -> set[int]:
        return {self.lock_state, self.lock_code}

    def set_mode(self, mode: int) -> None:
        self.interface_mode = mode

    def get_mode(self) -> int:
        return self.interface_mode
        
    def get_opst(self) -> int:
        return self.operational_status
    
    def set_opste(self, bit_weighting: int) -> None: 
        self.operational_status_enable = bit_weighting
    
    def get_opste(self) -> int: 
        return self.operational_status_enable
    
    def get_opstr(self) -> int:
        self.operational_status_return = self.operational_status
        self.operational_status = 0 # register is cleared when read
        return self.operational_status_return
    
    def set_psh(self, mode: int) -> None:
        if self.persistent_switch_enable == 1 and self.last_current == self.latest_current:
            self.persistent_switch_mode = mode
        else:
            self.persistent_switch_mode = 0
    
    def get_psh(self) -> bool:
        return self.persistent_switch_mode
    
    def get_pshis(self) -> int:
        return self.PSH_last_current
    
    def set_pshs(self, enable: int, current: int, delay: int) -> None:
        self.persistent_switch_enable = enable
        self.PSH_current = current
        self.PSH_delay_time = delay
        
    def get_pshs(self) -> set:
        return {self.persistent_switch_enable, self.PSH_current, self.PSH_delay_time}
    
    def set_qnch(self, enable: int, rate: float) -> None:
        self.quench_detection = enable
        self.step_limit = rate
    
    def get_qnch(self) -> set:
        return {self.quench_detection, self.step_limit}
    
    def set_rate(self, rate: float) -> None:
        self.current_ramp_rate = rate
    
    def get_rate(self) -> float:
        return self.current_ramp_rate
    
    def set_ratep(self, enable: int, rate: float) -> None:
        self.persistent_mode_rate = enable
        self.persistent_mode_ramp_rate = rate
    
    def get_ratep(self) -> set:
        return {self.persistent_mode_rate, self.persistent_mode_ramp_rate}
    
    def get_field(self) -> int:
        return self.field_output_reading
    
    def get_iout(self) -> int: 
        return self.latest_current
    
    def get_vrem(self) -> int:
        return self.remote_voltage
    
    def get_vout(self) -> int:
        return self.output_voltage
    
    def set_rseg(self, enable: int) -> None:
        self.ramp_segments = enable
    
    def get_rseg(self) -> bool:
        return self.ramp_segments
    
    def set_rsegs(self, segment: int, current: float, rate: float) -> None:
        if self.ramp_segments == 1:
            self.ramp_segments = segment
            match segment:
                case 1:
                    self.ramp_seg_one_current = current
                    self.ramp_seg_one_rate = rate
                case 2:
                    self.ramp_seg_two_current = current
                    self.ramp_seg_two_rate = rate
                case 3:
                    self.ramp_seg_three_current = current
                    self.ramp_seg_three_rate = rate
                case 4:
                    self.ramp_seg_four_current = current
                    self.ramp_seg_four_rate = rate
                case 5:
                    self.ramp_seg_five_current = current
                    self.ramp_seg_five_rate = rate

    
    def get_rsegs(self, ramp_segment_num: int) -> set:
        match ramp_segment_num:
            case 1:
                return{self.ramp_seg_one_current, self.ramp_seg_one_rate}
            case 2:
                return{self.ramp_seg_two_current, self.ramp_seg_two_rate}
            case 3:
                return{self.ramp_seg_three_current, self.ramp_seg_three_rate}
            case 4:
                return{self.ramp_seg_four_current, self.ramp_seg_four_rate}
            case 5:
                return{self.ramp_seg_five_current, self.ramp_seg_five_rate}
            case _:
                return None
    
    def set_setf(self, field: float) -> None:
        self.field_output_setting = field
    
    def get_setf(self) -> int:
        return self.field_output_setting
    
    def set_seti(self, current: float) -> None: ## set output current to ramp to
        self.output_current = current
    
    def get_seti(self) -> int:
        return self.output_current
    
    def set_setv(self, voltage: float) -> None: ## set output voltage
        self.output_compliance_voltage = voltage
    
    def get_setv(self) -> int: ## get output voltage
        return self.output_compliance_voltage
    
    def stop(self) -> None: ## stop output current
        self.output_current = 0
    
    def set_trig(self, value: float) -> None:
        self.trigger_output_current = value
    
    def get_trig(self) -> int:
        return self.trigger_output_current
    
    def set_xpgm(self, mode: int) -> None:
        self.external_program_mode = mode
    
    def get_xpgm(self) -> int:
        return self.external_program_mode
    
    
        
    
        
        
    def _get_state_handlers(self) -> dict[str, DefaultState]:
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self) -> str:
        return 'default'

    def _get_transition_handlers(self) -> OrderedDict:
        return OrderedDict([])
