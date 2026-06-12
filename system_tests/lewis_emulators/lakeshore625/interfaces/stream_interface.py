from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder


class FieldUnits(object):
    TESLA = object()

@has_log
class Lakeshore625StreamInterface(StreamInterface):
    
    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def __init__(self) -> None:
        super(Lakeshore625StreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder("clear").escape("*CLS").eos().build(),
            CmdBuilder("set_ese").escape("*ESE ").int().eos().build(),
            CmdBuilder("get_ese").escape("*ESE?").eos().build(),
            CmdBuilder("get_esr").escape("*ESR?").eos().build(),
            CmdBuilder("get_id").escape("*IDN?").eos().build(),
            CmdBuilder("set_opc").escape("*OPC").eos().build(),
            CmdBuilder("get_opc").escape("*OPC?").eos().build(),
            CmdBuilder("reset").escape("*RST").eos().build(),
            CmdBuilder("set_sre").escape("*SRE ").int().eos().build(),
            CmdBuilder("get_sre").escape("*SRE?").eos().build(),
            CmdBuilder("get_stb").escape("*STB?").eos().build(),
            CmdBuilder("trigger").escape("*TRG").eos().build(),
            CmdBuilder("get_test").escape("*TST?").eos().build(),
            CmdBuilder("default").escape("DFLT 99").eos().build(),
            CmdBuilder("clr_err").escape("ERCL").eos().build(),
            CmdBuilder("get_erst").escape("ERST?").eos().build(),
            CmdBuilder("set_erste").escape("ERSTE ").int().escape(",").int().escape(",").int()
            .eos().build(),
            CmdBuilder("get_erste").escape("ERSTE?").eos().build(),
            CmdBuilder("get_erstr").escape("ERSTR?").eos().build(),
            CmdBuilder("set_flds").escape("FLDS ").int().escape(",").float().eos().build(),
            CmdBuilder("get_flds").escape("FLDS?").eos().build(),
            CmdBuilder("set_lim").escape("LIMIT ").float().escape(",").float().escape(",").float()
            .eos().build(),
            CmdBuilder("get_lim").escape("LIMIT?").eos().build(),
            CmdBuilder("set_lock").escape("LOCK ").int().escape(",").int().eos().build(), 
            CmdBuilder("get_lock").escape("LOCK?").eos().build(),
            CmdBuilder("set_mode").escape("MODE ").int().eos().build(),
            CmdBuilder("get_mode").escape("MODE?").eos().build(),
            CmdBuilder("get_opst").escape("OPST?").eos().build(),
            CmdBuilder("set_opste").escape("OPSTE ").int().eos().build(),
            CmdBuilder("get_opste").escape("OPSTE?").eos().build(),
            CmdBuilder("get_opstr").escape("OPSTR?").eos().build(),
            CmdBuilder("set_psh").escape("PSH "),
            CmdBuilder("get_psh").escape("PSH?").eos().build(),
            CmdBuilder("get_pshis").escape("PSHIS?").eos().build(),
            CmdBuilder("set_pshs").escape("PSHS ").int().escape(",").int().escape(",")
            .int().eos().build(),
            CmdBuilder("get_pshs").escape("PSHS?").eos().build(),
            CmdBuilder("set_qnch").escape("QNCH ").int().escape(",").float().eos().build(),
            CmdBuilder("get_qnch").escape("QNCH?").eos().build(),
            CmdBuilder("set_rate").escape("RATE ").float().eos().build(),
            CmdBuilder("get_rate").escape("RATE?").eos().build(),
            CmdBuilder("set_ratep").escape("RATEP ").int().escape(",").float().eos().build(),
            CmdBuilder("get_ratep").escape("RATEP?").eos().build(),
            CmdBuilder("get_field").escape("RDGF?").eos().build(),
            CmdBuilder("get_iout").escape("RDGI?").eos().build(),
            CmdBuilder("get_vrem").escape("RDGRV?").eos().build(),
            CmdBuilder("get_vout").escape("RDGV?").eos().build(),
            CmdBuilder("set_rseg").escape("RSEG ").int().eos().build(),
            CmdBuilder("get_rseg").escape("RSEG?").eos().build(),
            # according to comments on protocol file by daresbury lab,
            # the following commands don't appear to work
            CmdBuilder("set_rsegs").escape("RSEGS ").int().escape(",").float().escape(",")
            .float().eos().build(),
            CmdBuilder("get_rsegs").escape("RSEGS? ").int().eos().build(),
            #####
            CmdBuilder("set_setf").escape("SETF ").float().eos().build(),
            CmdBuilder("get_setf").escape("SETF?").eos().build(),
            CmdBuilder("set_seti").escape("SETI ").float().eos().build(),
            CmdBuilder("get_seti").escape("SETI?").eos().build(),
            CmdBuilder("set_setv").escape("SETV ").float().eos().build(),
            CmdBuilder("get_setv").escape("SETV?").eos().build(),
            CmdBuilder("stop").escape("STOP").eos().build(),
            CmdBuilder("set_trig").escape("TRIG ").float().eos().build(),
            CmdBuilder("get_trig").escape("TRIG?").eos().build(),
            CmdBuilder("set_xpgm").escape("XPGM ").int().eos().build(),
            CmdBuilder("get_xpgm").escape("XPGM?").eos().build()
        }

    def handle_error(self, request: str, error: str) -> None:
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    def clear(self) -> None:
        self.device.clear()
    
    def set_ese(self, bit_weighting: int) -> None:
        self.device.set_ese(bit_weighting)
    
    def get_ese(self) -> int:
        return self.device.get_ese()

    def get_esr(self) -> int:
        return self.device.get_esr()

    def get_id(self) -> set:
        return self.device.get_id()

    def set_opc(self) -> None:
        self.device.set_opc()

    def get_opc(self) -> int:
        return self.device.get_opc()

    def reset(self) -> None:
        self.device.reset()

    def set_sre(self, bit_weighting: int) -> None:
        self.device.set_sre(bit_weighting)

    def get_sre(self) -> int:
        return self.device.get_sre()

    def get_stb(self) -> int: 
        return self.device.get_stb()

    def trigger(self) -> None:
        self.device.trigger()

    def get_test(self) -> int:
        return self.device.get_test()

    def default(self) -> None:
        self.device.default()

    def clr_err(self) -> None:
        self.device.clr_err()

    def get_erst(self) -> set[int]:
        return self.device.get_erst()

    def set_erste(self, hardware_bit_weighting: int, operational_bit_weighting: int, 
                  psh_bit_weighting: int) -> None:
        self.device.set_erste(hardware_bit_weighting, operational_bit_weighting, psh_bit_weighting)

    def get_erste(self) -> set[int]:
        return self.device.get_erste()

    def get_erstr(self) -> set[int]:
        return self.device.get_erstr()

    def set_flds(self, units: FieldUnits, constant: float) -> None:
        self.device.set_flds(units, constant)

    def get_flds(self) -> set:
        return self.device.get_flds()

    def set_lim(self, current: float, voltage: float, rate: float) -> None:
        self.device.set_lim(current, voltage, rate)

    def get_lim(self) -> set[int | float]:
        return self.device.get_lim()

    def set_lock(self, state: int, code: float) -> None:
        self.device.set_lock(state, code)

    def get_lock(self) -> set[int]:
        return self.device.get_lock()

    def set_mode(self, mode: int) -> None:
        self.device.set_mode(mode)
    
    def get_mode(self) -> int:
        return self.device.get_mode()
    
    def get_opst(self) -> int:
        return self.device.get_opst()
    
    def set_opste(self, bit_weighting: int) -> None:
        self.device.set_opste(bit_weighting)
        
    def get_opste(self) -> int:
        return self.device.get_opste()

    def get_opstr(self) -> int:
        return self.device.get_opstr()

    def set_psh(self, mode: int) -> None:
        self.device.set_psh(mode)

    def get_psh(self) -> bool:
        return self.device.get_psh()

    def get_pshis(self) -> int:
        return self.device.get_pshis()

    def set_pshs(self, enable: int, current: int, delay: int) -> None:
        self.device.set_pshs(enable, current, delay)

    def get_pshs(self) -> set:
        return self.device.get_pshs()

    def set_qnch(self, enable: int, rate: float) -> None:
        self.device.set_qnch(enable, rate)

    def get_qnch(self) -> set:
        return self.device.get_qnch()

    def set_rate(self, rate: float) -> None:
        self.device.set_rate(rate)

    def get_rate(self) -> float:
        return self.device.get_rate()
    
    def set_ratep(self, enable: int, rate: float) -> None:
        self.device.set_ratep(enable, rate)
    
    def get_ratep(self) -> set:
        return self.device.get_ratep()

    def get_field(self) -> int:
        return self.device.get_field()
        
    def get_iout(self) -> int:
        return self.device.get_iout()
    
    def get_vrem(self) -> int:
        return self.device.get_vrem()
    
    def get_vout(self) -> int:
        return self.device.get_vout()
    
    def set_rseg(self, enable: int) -> None:
        self.device.set_rseg(enable)
    
    def get_rseg(self) -> bool:
        return self.device.get_rseg()
    
    def set_rsegs(self, segment: int, current: float, rate: float) -> None:
        self.device.set_rsegs(segment, current, rate)
    
    def get_rsegs(self, ramp_segment_num: int) -> set:
        return self.device.get_rsegs() # come back to

    def set_setf(self, field: float) -> None:
        self.device.set_setf(field)

    def get_setf(self) -> int:
        return self.device.get_setf()

    def set_seti(self, current: float) -> None:
        self.device.set_seti(current)

    def get_seti(self) -> int:
        return self.device.get_seti()

    def set_setv(self, voltage: float) -> None:
        self.device.set_setv(voltage)

    def get_setv(self) -> int:
        return self.device.get_setv()

    def stop(self) -> None:
        self.device.stop()

    def set_trig(self, value: float) -> None:
        self.device.set_trig(value)

    def get_trig(self) -> int:
        return self.device.get_trig()

    def set_xpgm(self, mode: int) -> None:
        self.device.set_xpgm(mode)

    def get_xpgm(self) -> int:
        return self.device.get_xpgm()


    def get_status(self) -> int:
        status = self.device.status_byte_register * 64
        return status 

