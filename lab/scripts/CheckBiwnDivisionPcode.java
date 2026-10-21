// Compare installed Sleigh DIVU and the original BIWN helper with saved CPU fixtures.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.io.*;
import java.util.*;
import com.google.gson.*;

public class CheckBiwnDivisionPcode extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Supply saved CPU fixture report and output JSON");
        JsonObject fixtures;
        try (Reader reader = new FileReader(args[0])) {
            fixtures = JsonParser.parseReader(reader).getAsJsonObject();
        }
        if (!fixtures.get("original_candidate_sha256").getAsString().equals(
                "52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453"))
            throw new IllegalArgumentException("Unexpected candidate fixtures");
        List<Map<String,Object>> results = new ArrayList<>();
        int operationFailures = 0, helperFailures = 0;
        for (JsonElement element : fixtures.getAsJsonArray("division_cases")) {
            JsonObject fixture = element.getAsJsonObject();
            long numerator = fixture.get("numerator").getAsLong();
            long divisor = fixture.get("divisor").getAsLong();
            long expected = fixture.get("quotient").getAsLong();
            if (divisor == 0) throw new IllegalArgumentException("Zero divisor is outside this experiment");
            for (long initialVF : new long[]{0,1}) {
                EmulatorHelper emu = new EmulatorHelper(currentProgram);
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("numerator",numerator); row.put("divisor",divisor); row.put("initial_VF",initialVF);
                try {
                    emu.writeRegister("D0",0xa5a50000L | divisor);
                    emu.writeRegister("D1",numerator);
                    emu.writeRegister("D2",0x12345678L);
                    emu.writeRegister("D3",0x9abcdef0L);
                    emu.writeRegister("VF",initialVF);
                    emu.writeRegister("CF",1L);
                    emu.writeRegister("XF",1L);
                    emu.writeRegister(emu.getStackPointerRegister(),0x1ff000L);
                    emu.writeMemoryValue(toAddr(0x1ff000),4,0x1ffe00);
                    emu.getEmulator().setExecuteAddress(0xd1e0);
                    if (!emu.step(monitor)) throw new IllegalStateException(emu.getLastError());
                    long fullQuotient = numerator / divisor;
                    boolean overflow = fullQuotient > 65535;
                    long expectedDestination = overflow ? numerator : ((numerator % divisor) << 16) | fullQuotient;
                    long actualDestination = emu.readRegister("D1").longValue() & 0xffffffffL;
                    long actualVF = emu.readRegister("VF").longValue();
                    boolean instructionPass = actualDestination == expectedDestination &&
                        actualVF == (overflow ? 1 : 0) && emu.readRegister("CF").longValue() == 0 &&
                        emu.readRegister("XF").longValue() == 1;
                    if (!overflow) instructionPass &=
                        emu.readRegister("NF").longValue() == ((fullQuotient & 0x8000) != 0 ? 1 : 0) &&
                        emu.readRegister("ZF").longValue() == (fullQuotient == 0 ? 1 : 0);
                    row.put("word_DIVU_matches_defined_nonzero_semantics",instructionPass);
                    row.put("DIVU_destination",actualDestination); row.put("DIVU_VF",actualVF);
                    row.put("overflow",overflow);
                    if (!instructionPass) operationFailures++;
                    int steps = 1;
                    while (emu.getExecutionAddress().getOffset() != 0x1ffe00 && steps < 128) {
                        long pc = emu.getExecutionAddress().getOffset();
                        if (pc < 0xd1e0 || pc >= 0xd206) throw new IllegalStateException("Unexpected code address " + Long.toHexString(pc));
                        if (!emu.step(monitor)) throw new IllegalStateException(emu.getLastError());
                        steps++;
                    }
                    long actual = emu.readRegister("D1").longValue() & 0xffffffffL;
                    boolean helperPass = emu.getExecutionAddress().getOffset() == 0x1ffe00 && actual == expected &&
                        emu.readRegister("D2").longValue() == 0x12345678L &&
                        emu.readRegister("D0").longValue() == (0xa5a50000L | divisor) &&
                        emu.readRegister(emu.getStackPointerRegister()).longValue() == 0x1ff004;
                    row.put("helper_matches_saved_CPU_quotient_and_preserved_registers",helperPass);
                    row.put("expected_quotient",expected); row.put("actual_quotient",actual); row.put("steps",steps);
                    if (!helperPass) helperFailures++;
                } catch (Exception error) {
                    row.put("error",error.toString());
                    operationFailures++; helperFailures++;
                } finally { emu.dispose(); }
                results.add(row);
            }
        }
        Map<String,Object> report = new LinkedHashMap<>();
        report.put("language",currentProgram.getLanguageID().toString());
        report.put("compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        report.put("cases",results.size()); report.put("DIVU_failures",operationFailures);
        report.put("helper_failures",helperFailures); report.put("results",results);
        report.put("scope","P-code execution of nonzero word DIVU and original helper against saved Unicorn/portable-C CPU fixtures. N/Z on overflow undefined and untested; zero-divisor traps and whole game excluded.");
        try (PrintWriter output = new PrintWriter(args[1])) {
            new GsonBuilder().setPrettyPrinting().create().toJson(report,output);
        }
        println("DIVU fixture cases="+results.size()+", operation failures="+operationFailures+", helper failures="+helperFailures);
    }
}
