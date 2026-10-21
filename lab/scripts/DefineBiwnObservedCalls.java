// Conservative entry candidates: sampled direct call sites and sampled targets.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;

public class DefineBiwnObservedCalls extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Supply plan and report JSON paths");
        JsonObject plan = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        List<Map<String,Object>> results = new ArrayList<>();
        for (JsonElement element : plan.getAsJsonArray("candidates")) {
            JsonObject candidate = element.getAsJsonObject();
            Address entry = toAddr(candidate.get("address").getAsLong());
            Function containing = getFunctionContaining(entry);
            Map<String,Object> row = new LinkedHashMap<>(); row.put("address",entry.toString());
            if (containing != null) {
                row.put("status","retained_existing_function_body");
                row.put("containing_entry",containing.getEntryPoint().toString());
            } else {
                Function function = createFunction(entry,"observed_call_candidate_"+entry);
                if (function == null) throw new IllegalStateException("Cannot create candidate at "+entry);
                function.setComment("Analyst entry candidate: direct call site and target PC sampled in assisted emulator; first post-frame bytes match candidate. Body inferred from existing decoded flow; original boundary/name/ABI unverified. Evidence: "+candidate.get("calls").toString());
                row.put("status","created_direct_call_entry_candidate");
                row.put("name",function.getName());
                row.put("body_bytes",function.getBody().getNumAddresses());
                row.put("body_ranges",function.getBody().getNumAddressRanges());
            }
            results.add(row);
        }
        Map<String,Object> report = new LinkedHashMap<>();
        report.put("results",results);
        report.put("scope","Direct-call evidence supports entry candidates; inferred function bodies, original names and ABI remain unverified.");
        try (PrintWriter output = new PrintWriter(args[1])) {
            new GsonBuilder().setPrettyPrinting().create().toJson(report,output);
        }
    }
}
