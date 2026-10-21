// Separate-copy shared-memory volatility experiment; not hardware validation.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.listing.CodeUnit;
import java.io.File;
import java.io.PrintWriter;
import java.util.*;
import com.google.gson.GsonBuilder;

public class AnnotateBiwnSharedVolatile extends GhidraScript {
 public void run() throws Exception {
  String[] args = getScriptArgs();
  if (args.length != 1) throw new IllegalArgumentException("Supply annotation report path");
  var start = toAddr(0xf03200L);
  if (currentProgram.getMemory().getBlock(start) != null)
   throw new IllegalStateException("External shared range already mapped; preserve baseline");
  MemoryBlock block = currentProgram.getMemory().createUninitializedBlock("BIWN_shared_words_candidate", start, 32, false);
  block.setRead(true); block.setWrite(true); block.setExecute(false); block.setVolatile(true);
  block.setComment("Analyst annotation: shared external words may change asynchronously. No initial values/device implementation/hardware behavior assumed.");
  List<Map<String,Object>> words = new ArrayList<>();
  for (long offset = 0; offset < 32; offset += 4) {
   var address = start.add(offset);
   createData(address, UnsignedIntegerDataType.dataType);
   String name = String.format("shared_word_%08x_candidate", address.getOffset());
   createLabel(address, name, true, SourceType.USER_DEFINED);
   currentProgram.getListing().setComment(address, CodeUnit.PLATE_COMMENT,
     "Analyst volatile shared-memory candidate; not an original symbol or validated device register.");
   Map<String,Object> row = new LinkedHashMap<>();
   row.put("address", address.toString()); row.put("bytes", 4); row.put("label", name);
   words.add(row);
  }
  Map<String,Object> report = new LinkedHashMap<>();
  report.put("start", block.getStart().toString()); report.put("end_inclusive", block.getEnd().toString());
  report.put("volatile", block.isVolatile()); report.put("initialized", block.isInitialized());
  report.put("execute", block.isExecute()); report.put("words", words);
  report.put("scope", "Separate project annotation only. Uninitialized volatile words preserve possible asynchronous changes; no device execution or original ABI reconstruction.");
  try (PrintWriter stream = new PrintWriter(new File(args[0]))) {
   new GsonBuilder().setPrettyPrinting().create().toJson(report, stream);
  }
 }
}
