// Add only individually observed instruction boundaries; do not infer functions.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import com.google.gson.*;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class AddBiwnObservedInstructions extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Supply plan and report JSON paths");
        JsonObject plan = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        byte[] image = new byte[0xfc000];
        if (currentProgram.getMemory().getBytes(toAddr(0x4000), image) != image.length)
            throw new IllegalStateException("Image incomplete");
        String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image));
        if (!hash.equals(plan.get("stage_sha256").getAsString()))
            throw new IllegalStateException("Image hash differs");
        int functionCount = currentProgram.getFunctionManager().getFunctionCount();
        List<Map<String,Object>> results = new ArrayList<>();
        Listing listing = currentProgram.getListing();
        for (JsonElement element : plan.getAsJsonArray("seeds")) {
            monitor.checkCancelled();
            JsonObject seed = element.getAsJsonObject();
            Address address = toAddr(seed.get("address").getAsLong());
            int length = seed.get("size").getAsInt();
            Address end = address.add(length - 1);
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("address", address.toString());
            Data data = listing.getDefinedDataContaining(address);
            if (data != null) {
                row.put("status", "defined_data_conflict_retained");
                row.put("data_start", data.getAddress().toString());
                row.put("data_length", data.getLength());
                results.add(row); continue;
            }
            DisassembleCommand command = new DisassembleCommand(address, new AddressSet(address,end), false);
            command.enableCodeAnalysis(false);
            boolean applied = command.applyTo(currentProgram,monitor);
            Instruction instruction = listing.getInstructionAt(address);
            if (!applied || instruction == null) {
                row.put("status", "not_decoded"); row.put("message", command.getStatusMsg());
            } else {
                String bytes = HexFormat.of().formatHex(instruction.getBytes());
                if (instruction.getLength() != length || !bytes.equals(seed.get("bytes").getAsString()))
                    throw new IllegalStateException("Decoder boundary/bytes differ at " + address);
                row.put("status", "decoded_exact_observed_instruction");
                row.put("size", length); row.put("bytes", bytes);
                row.put("assembly", instruction.toString());
                listing.setComment(address, CodeUnit.EOL_COMMENT,
                    "Observed CPU PC; first post-frame bytes matched static candidate. Incomplete sampled coverage, not function-boundary or hardware proof.");
            }
            results.add(row);
        }
        if (functionCount != currentProgram.getFunctionManager().getFunctionCount())
            throw new IllegalStateException("Unexpected function creation");
        Map<String,Object> report = new LinkedHashMap<>();
        report.put("stage_sha256",hash); report.put("results",results);
        report.put("function_count_unchanged",functionCount);
        report.put("scope","Only sampled instruction boundaries; analysis disabled, no functions inferred, conflicting defined data retained.");
        try (PrintWriter output = new PrintWriter(args[1])) {
            new GsonBuilder().setPrettyPrinting().create().toJson(report,output);
        }
    }
}
