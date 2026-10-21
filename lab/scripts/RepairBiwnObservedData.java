// Reclassify only a contiguous, stable observed CPU instruction interval.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;

public class RepairBiwnObservedData extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Supply plan and output JSON");
        JsonObject plan = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        byte[] image = new byte[0xfc000];
        if (currentProgram.getMemory().getBytes(toAddr(0x4000), image) != image.length)
            throw new IllegalStateException("Incomplete image");
        String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image));
        if (!hash.equals(plan.get("stage_sha256").getAsString())) throw new IllegalStateException("Image changed");
        Listing listing = currentProgram.getListing();
        Address start = toAddr(plan.get("start").getAsLong());
        Address end = toAddr(plan.get("end_inclusive").getAsLong());
        AddressSet selected = new AddressSet(start,end);
        if (listing.getInstructionContaining(start) != null || listing.getInstructionContaining(end) != null ||
            listing.getInstructions(selected,true).hasNext())
            throw new IllegalStateException("Selected range overlaps retained instruction");
        List<Map<String,Object>> previousUnits = new ArrayList<>();
        CodeUnitIterator units = listing.getCodeUnits(selected,true);
        while (units.hasNext()) {
            CodeUnit unit = units.next();
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("address",unit.getAddress().toString()); row.put("bytes",unit.getLength());
            row.put("description",unit.toString()); row.put("class",unit.getClass().getSimpleName());
            previousUnits.add(row);
        }
        long cursor = start.getOffset();
        for (JsonElement element : plan.getAsJsonArray("seeds")) {
            JsonObject seed=element.getAsJsonObject();
            if (seed.get("address").getAsLong() != cursor) throw new IllegalStateException("Noncontiguous plan");
            cursor += seed.get("size").getAsInt();
        }
        if (cursor != end.getOffset()+1) throw new IllegalStateException("Plan does not cover selected range");
        listing.clearCodeUnits(start,end,false);
        List<Map<String,Object>> results = new ArrayList<>();
        for (JsonElement element : plan.getAsJsonArray("seeds")) {
            monitor.checkCancelled(); JsonObject seed=element.getAsJsonObject();
            Address address=toAddr(seed.get("address").getAsLong());
            int length=seed.get("size").getAsInt();
            DisassembleCommand command=new DisassembleCommand(address,new AddressSet(address,address.add(length-1)),false);
            command.enableCodeAnalysis(false);
            if (!command.applyTo(currentProgram,monitor)) throw new IllegalStateException(command.getStatusMsg());
            Instruction instruction=listing.getInstructionAt(address);
            if (instruction == null || instruction.getLength()!=length ||
                !HexFormat.of().formatHex(instruction.getBytes()).equals(seed.get("bytes").getAsString()))
                throw new IllegalStateException("Instruction differs from stable observed bytes");
            listing.setComment(address,CodeUnit.EOL_COMMENT,"Analyst reclassification: CPU PC sampled twice in long assisted-emulator run; stable first16postframe bytes match original candidate. No ABI, instruction-time RAM or hardware proof.");
            Map<String,Object> row=new LinkedHashMap<>(); row.put("address",address.toString());
            row.put("size",length); row.put("bytes",seed.get("bytes").getAsString());
            row.put("assembly",instruction.toString()); row.put("status","observed_instruction_reclassified_from_data");
            results.add(row);
        }
        Map<String,Object> report=new LinkedHashMap<>();report.put("stage_sha256",hash);
        report.put("previous_code_units",previousUnits);report.put("results",results);
        report.put("scope","Only selected14bytes reclassified in project copy; no memory bytes or existing instructions intentionally changed.");
        try(PrintWriter output=new PrintWriter(args[1])) {new GsonBuilder().setPrettyPrinting().create().toJson(report,output);}
    }
}
