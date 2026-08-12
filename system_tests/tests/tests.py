import unittest


from parameterized import parameterized
from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim

DEVICE_PREFIX = "LKSH625_01" 


IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("LKSH625"),
        "macros": {},
        "emulator": "lakeshore625",
    },
]


TEST_MODES = [TestModes.RECSIM, TestModes.DEVSIM]

### USEFUL FUNCTIONS ###

def _set_local_mode(ca,mode):
    ca.set_pv_value("MODE:SP", mode)

class Lakeshore625Tests(unittest.TestCase):
    """
    Tests for the _Device_ IOC.
    """
    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("lakeshore625", DEVICE_PREFIX)
        self.ca = ChannelAccess(default_timeout = 20, device_prefix=DEVICE_PREFIX, default_wait_time = 0.0)

        #self.ca.wait_for("DISABLE", timeout=30)
        
    
    # RDGI
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_current_set_THEN_current_can_be_read_back(self):
        self._lewis.backdoor_set_on_device("latest_current", 40.000)
        self.ca.assert_that_pv_is_number("CURR:MAG", 40.000)

    # RDGV
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_voltage_set_THEN_voltage_can_be_read_back(self):
        self._lewis.backdoor_set_on_device("output_voltage", 40.000)
        self.ca.assert_that_pv_is_number("VOLT:SUP", 40.000)

    # SETI
    def test_WHEN_setting_current_setpoint_THEN_current_ramps_to_setpoint(self):
        self.ca.set_pv_value("CURR:SP", 40.000)
        self.ca.assert_that_pv_is_number("CURR:SP", 40.000)

    # SETV
    def test_WHEN_setting_compliance_voltage_THEN_compliance_voltage_can_be_read_back(self):
        self.ca.set_pv_value("VOLT:COM:SP", 3.000)
        self.ca.assert_that_pv_is_number("VOLT:COM:SP", 3.000)

    # LIMIT
    def test_WHEN_getting_limits_THEN_warnings_set(self):
        self.ca.set_pv_value("LIMIT:CURR:SP", 40.000)
        self.ca.set_pv_value("LIMIT:VOLT:SP", 3.000)
        self.ca.set_pv_value("LIMIT:RATE:SP", 40.000)
        self.ca.assert_that_pv_is_number("LIMIT:CURR:SP", 40.000)
        self.ca.assert_that_pv_is_number("LIMIT:VOLT:SP", 3.000)
        self.ca.assert_that_pv_is_number("LIMIT:RATE:SP", 40.000)
        self.ca.process_pv("LIMIT:SEQ:SP")
        # Check sequence of warning limits
        # Voltage
        self.ca.assert_that_pv_is_number("VOLT:MAG.HIGH", 3.000)
        self.ca.assert_that_pv_is_number("VOLT:SUP.HIGH", 3.000)
        self.ca.assert_that_pv_is_number("VOLT:COM.HIGH", 3.000)
        self.ca.assert_that_pv_is_number("VOLT:MAG.LOW", -3.000)
        # Current
        self.ca.assert_that_pv_is_number("CURR.HIGH", 40.000)
        self.ca.assert_that_pv_is_number("TRIG.HIGH", 40.000)
        self.ca.assert_that_pv_is_number("CURR.LOW", -40.000)
        # Ramprate
        self.ca.assert_that_pv_is_number("RAMPRATE:SP.HIGH", 40.000)
        self.ca.assert_that_pv_is_number("RAMPRATE:PM.HIGH", 40.000)

    @skip_if_recsim("Cannot connect to device in recsim")
    # *STB?
    def test_GIVEN_MSS_set_WHEN_read_THEN_MSS_is_as_expected(self):
        self._lewis.backdoor_set_on_device("master_summ_status_bit", 1)
        self.ca.assert_that_pv_is("STAT:BYTE", 1)

    # CLEAR
    def test_GIVEN_interface_cleared_THEN_errors_cleared(self):
        self.ca.set_pv_value("ERROR:HARDWARE:EVENT", 1)
        self.ca.set_pv_value("ERROR:OP:EVENT", 1)
        self.ca.set_pv_value("ERROR:PSH:EVENT", 1)
        self.ca.set_pv_value("STAT:REG:SP", 1)
        self.ca.set_pv_value("STAT:OP:REG:SP", 1)
        self.ca.process_pv("STAT:CLEAR")
        self.ca.assert_that_pv_is("ERROR:CLEAR:CMD", "Clear") 
        self.ca.assert_that_pv_is("ERROR:HARDWARE:EVENT", 0)
        self.ca.assert_that_pv_is("ERROR:OP:EVENT", 0)
        self.ca.assert_that_pv_is("ERROR:PSH:EVENT", 0)
        self.ca.assert_that_pv_is("INTER:CLEAR", "Clear")
        self.ca.assert_that_pv_is("STAT:REG:SP", 0)
        self.ca.assert_that_pv_is("STAT:OP:REG:SP", 0)

    # when local/remote mode then mode is local/remote
    # MODE
    def test_WHEN_set_local_mode_THEN_mode_is_local(self):
        _set_local_mode(self.ca, "Local") 
        self.ca.assert_that_pv_is("MODE:SP", "Local")

    # MODE
    def test_WHEN_set_remote_mode_THEN_mode_is_remote(self):
        _set_local_mode(self.ca, "Remote") 
        self.ca.assert_that_pv_is("MODE:SP", "Remote")

    # FLDS
    def test_WHEN_setting_field_parameter_setpoint_THEN_field_parameter_read_back_correctly(self):
        self.ca.set_pv_value("FIELD:PARAM:CONSTANT:SP", 5.500)
        self.ca.set_pv_value("FIELD:PARAM:UNITS:SP", "kG/A")
        self.ca.assert_that_pv_is_number("FIELD:PARAM:CONSTANT:SP", 5.500)
        self.ca.assert_that_pv_is("FIELD:PARAM:UNITS:SP", "kG/A")

    # LOCK
    def test_WHEN_setting_lock_THEN_lock_read_back_correctly(self):
        self.ca.set_pv_value("LOCK:SP", "Lock")
        self.ca.assert_that_pv_is("LOCK:SP", "Lock")

    # OPST?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_GIVEN_operational_status_bits_set_THEN_read_back_correct(self):
        self._lewis.backdoor_set_on_device("operational_status", 0)
        self.ca.assert_that_pv_is("STAT:OP", 0)

    # OPSTE / OPSTE?
    def test_GIVEN_operational_status_enable_set_THEN_operational_status_enable_read_back(self):
        self.ca.set_pv_value("LIMIT:CURR:SP", 5.000)
        self.ca.assert_that_pv_is_number("LIMIT:CURR:SP", 5.000)
        #self.ca.set_pv_value(":STAT:OP:ENABLE:SP", 2)
        #self.ca.assert_that_pv_is(":STAT:OP:ENABLE", 2)

    # OPSTR?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_GIVEN_operational_status_register_set_THEN_operational_status_register_read_back(self):
        self._lewis.backdoor_set_on_device("operational_status", 6)
        self.ca.assert_that_pv_is("STAT:OP:REG", 6)

    # PSH / PSH?
    def test_WHEN_psh_mode_set_THEN_psh_mode_read_back_correctly(self):
        self.ca.set_pv_value("PSH:ENABLE", "Enabled")
        self.ca.set_pv_value("STAT:PSH:SP", "On")
        self.ca.assert_that_pv_is("STAT:PSH:SP", "On")

    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_last_current_different_to_latest_current_THEN_PSH_doesnt_turn_on(self):
        self._lewis.backdoor_set_on_device("last_current", 40.000)
        self._lewis.backdoor_set_on_device("latest_current", 30.000)
        self.ca.set_pv_value("PSH:ENABLE", "Enabled")
        self.ca.set_pv_value("STAT:PSH:SP", "On")
        self.ca.assert_that_pv_is("STAT:PSH:SP", "Off")

    # PSHIS
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_last_current_set_THEN_last_current_can_be_read_back(self):
        self._lewis.backdoor_set_on_device("last_current", 40.000)
        self.ca.assert_that_pv_is_number("CURR:PSH:LAST", 40.000)

    # PSHS / PSHS?
    def test_WHEN_PSH_parameters_set_THEN_PSH_parameters_are_read_back_correctly(self):
        self.ca.set_pv_value("PSH:ENABLE:SP", "Enabled")
        self.ca.set_pv_value("PSH:CURR:SP", 80)
        self.ca.set_pv_value("PSH:TIME:SP", 20)

        self.ca.assert_that_pv_is("PSH:ENABLE:SP", "Enabled")
        self.ca.assert_that_pv_is("PSH:CURR:SP", 80)
        self.ca.assert_that_pv_is("PSH:TIME:SP", 20)

    # QNCH / QNCH?
    def test_WHEN_quench_detection_parameters_set_THEN_quench_detection_parameters_read_back_correctly(self):
        self.ca.set_pv_value("QUENCH:ENABLE:SP", "Enabled")
        self.ca.set_pv_value("QUENCH:RATE:SP", 5.000)

        self.ca.assert_that_pv_is("QUENCH:ENABLE:SP", "Enabled")
        self.ca.assert_that_pv_is_number("QUENCH:RATE:SP", 5.000)

    # RATE / RATE?
    def test_WHEN_ramp_rate_set_THEN_ramp_rate_read_back_correctly(self):
        self.ca.set_pv_value("RAMPRATE:SP", 50.000)
        self.ca.assert_that_pv_is_number("RAMPRATE:SP", 50.000)

    # RATEP / RATEP?
    def test_WHEN_persistent_mode_ramprate_param_set_THEN_persistent_mode_ramprate_param_read_back_correctly(self):
        self.ca.set_pv_value("RAMPRATE:PM:ENABLE:SP", "Enabled")
        self.ca.set_pv_value("RAMPRATE:PM:SP", 50.000)

        self.ca.assert_that_pv_is("RAMPRATE:PM:ENABLE:SP", "Enabled")
        self.ca.assert_that_pv_is_number("RAMPRATE:PM:SP", 50.000)

    # RDGF?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_field_set_THEN_field_read_back_correctly(self):
        self.ca.set_pv_value("FIELD:PARAM:CONSTANT:SP", 5.500)
        self._lewis.backdoor_set_on_device("latest_current", 40.000)
        self.ca.assert_that_pv_is_number("FIELD:MAG", 220.000)

    # RDGRV?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_remote_voltage_set_THEN_remote_voltage_read_back_correctly(self):
        self._lewis.backdoor_set_on_device("remote_voltage", 40.000)
        self.ca.assert_that_pv_is_number("VOLT:MAG", 40.000)

    # RSEG / RSEG?
    def test_WHEN_ramp_segment_enable_set_THEN_ramp_segment_enable_read_back_correctly(self):
        self.ca.set_pv_value("RAMPSEG:ENABLE:SP", "Enabled")
        self.ca.assert_that_pv_is("RAMPSEG:ENABLE:SP", "Enabled")

    # RSEGS / RSEGS?
    @parameterized.expand(
        [
            "1", "2", "3", "4", "5"
        ]
    )
    @skip_if_recsim("Cannot catch errors in recsim")
    def test_WHEN_ramp_segment_parameters_set_THEN_ramp_segment_parameters_read_back_correctly(self, ramp_segment):
        self.ca.set_pv_value("RAMPSEG:ENABLE:SP", "Enabled") # enable ramp segments -> RSEG
        self.ca.set_pv_value("RAMPSEG" + ramp_segment + ":SP", ramp_segment)
        self.ca.set_pv_value("RAMPSEG" + ramp_segment + ":CURR:SP", 40.000)
        self.ca.set_pv_value("RAMPSEG" + ramp_segment + ":RAMPRATE:SP", 70.000)

        # # self.ca.assert_that_pv_is("RAMPSEG" + ramp_segment, ramp_segment) 
        self.ca.assert_that_pv_is_number("RAMPSEG" + ramp_segment + "CURR:SP", 40.000)
        self.ca.assert_that_pv_is_number("RAMPSEG" + ramp_segment + "RAMPRATE:SP", 70.000)

    # SETF / SETF?
    def test_WHEN_output_field_set_THEN_output_field_read_back_correctly(self):
        self.ca.set_pv_value("FIELD:SP", 300.00)
        self.ca.assert_that_pv_is_number("FIELD:SP", 300.00)
        
    # TRIG / TRIG?
    def test_WHEN_trigger_current_set_THEN_trigger_current_read_back_correctly(self):
        self.ca.set_pv_value("TRIG:SP", -40.000)
        self.ca.assert_that_pv_is_number("TRIG:SP", -40.000)

    # XPGM / XPGM
    @parameterized.expand(
        [
            "Internal", "External", "Sum"
        ]
    )
    def test_WHEN_external_program_mode_set_THEN_external_program_mode_read_back_correctly(self, mode):
        self.ca.set_pv_value("SEL:PROG:SP", mode)
        self.ca.assert_that_pv_is("SEL:PROG:SP", mode)

    # SRE / SRE?
    def test_WHEN_service_request_enable_set_THEN_service_request_enable_read_back(self):
        self.ca.set_pv_value("STAT:REQ:SP", 17)
        self.ca.assert_that_pv_is("STAT:REQ:SP", 17)
    # TRG x
    # TST?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_errors_set_THEN_test_returns_errors(self):
        self._lewis.backdoor_set_on_device("self_test", "Error")
        self.ca.assert_that_pv_is("TEST", "Error")

    # ERST?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_error_bit_weighting_set_THEN_error_bit_weighting_returned(self):
        self._lewis.backdoor_set_on_device("operational_errors", 2)
        self._lewis.backdoor_set_on_device("PSH_errors", 1)
        self._lewis.backdoor_set_on_device("hardware_errors", 4)
        self.ca.assert_that_pv_is("ERROR:STAT:OP", 2)
        self.ca.assert_that_pv_is("ERROR:STAT:PSH", 1)
        self.ca.assert_that_pv_is("ERROR:STAT:HARDWARE", 4)

    # ERSTE / ERSTE?
    def test_WHEN_error_status_enable_set_THEN_errors_read_back_correctly(self):
        self.ca.set_pv_value("ERROR:HARDWARE:SP", 1)
        self.ca.set_pv_value("ERROR:OP:SP", 2)
        self.ca.set_pv_value("ERROR:PSH:SP", 4)
        self.ca.assert_that_pv_is("ERROR:HARDWARE:SP", 1)
        self.ca.assert_that_pv_is("ERROR:OP:SP", 2)
        self.ca.assert_that_pv_is("ERROR:PSH:SP", 4)

    # ERSTR?
    @skip_if_recsim("Cannot connect to device in recsim")
    def test_WHEN_error_status_register_set_THEN_error_status_register_read_back_correctly(self):
        self._lewis.backdoor_set_on_device("operational_errors", 2)
        self._lewis.backdoor_set_on_device("PSH_errors", 1)
        self._lewis.backdoor_set_on_device("hardware_errors", 4)
        self.ca.assert_that_pv_is("ERROR:OP:REG", 2)
        self.ca.assert_that_pv_is("ERROR:PSH:REG", 1)
        self.ca.assert_that_pv_is("ERROR:HARDWARE:REG", 4)



