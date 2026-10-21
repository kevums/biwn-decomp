// Export decompiler approximations and assembly for review.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.InstructionIterator;
import java.io.File;
import java.io.PrintWriter;
import java.util.*;
import com.google.gson.GsonBuilder;
public class ExportDecomp extends GhidraScript {
 public void run() throws Exception {
  String[] args = getScriptArgs();
  if (args.length != 1) throw new IllegalArgumentException("Supply output directory");
  File out = new File(args[0]); out.mkdirs();
  DecompInterface decomp = new DecompInterface();
  Map<String,Object> manifest = new LinkedHashMap<>();
  manifest.put("language", currentProgram.getLanguageID().toString());
  manifest.put("language_description", currentProgram.getLanguage().getLanguageDescription().getDescription());
  manifest.put("compiler_spec", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
  manifest.put("integer_bytes", currentProgram.getDataTypeManager().getDataOrganization().getIntegerSize());
  manifest.put("pointer_bytes", currentProgram.getDataTypeManager().getDataOrganization().getPointerSize());
  manifest.put("warning", "Decompiler approximation under selected language/ABI. Not original source or runtime verification.");
  List<Map<String,Object>> functionRows = new ArrayList<>();
  List<Map<String,Object>> instructionRows = new ArrayList<>();
  try {
   if (!decomp.openProgram(currentProgram)) throw new RuntimeException("Could not open program for decompilation");
   try (PrintWriter c = new PrintWriter(new File(out,"decompiled.c"));
        PrintWriter asm = new PrintWriter(new File(out,"listing.asm"))) {
    c.println("/* Ghidra approximation. Not original source; validate against binary behavior. */");
    c.println("/* Language: " + currentProgram.getLanguageID() + " */");
    FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
    while (functions.hasNext() && !monitor.isCancelled()) {
     Function f = functions.next();
     c.println("/* Address " + f.getEntryPoint() + " */");
     DecompileResults r = decomp.decompileFunction(f,60,monitor);
     Map<String,Object> row = new LinkedHashMap<>();
     row.put("address", f.getEntryPoint().toString()); row.put("name", f.getName());
     row.put("decompiled", r.decompileCompleted()); row.put("error", r.getErrorMessage());
     functionRows.add(row);
     if (r.decompileCompleted() && r.getDecompiledFunction()!=null) c.println(r.getDecompiledFunction().getC());
     else c.println("/* FAILED: " + r.getErrorMessage() + " */");
    }
    InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
    while (instructions.hasNext() && !monitor.isCancelled()) {
     var i = instructions.next(); asm.println(i.getAddress()+": "+i);
     Map<String,Object> row = new LinkedHashMap<>();
     StringBuilder bytes = new StringBuilder();
     for (byte b : i.getBytes()) bytes.append(String.format("%02x", b & 0xff));
     row.put("address", i.getAddress().toString()); row.put("size", i.getLength());
     row.put("bytes", bytes.toString()); row.put("assembly", i.toString());
     instructionRows.add(row);
    }
   }
   manifest.put("functions", functionRows); manifest.put("instructions", instructionRows);
   manifest.put("cancelled", monitor.isCancelled());
   try (PrintWriter metadata = new PrintWriter(new File(out,"manifest.json"))) {
    new GsonBuilder().setPrettyPrinting().create().toJson(manifest, metadata);
   }
  } finally { decomp.dispose(); }
 }
}
