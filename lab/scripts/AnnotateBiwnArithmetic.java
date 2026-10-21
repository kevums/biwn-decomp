// Evidence-based local signatures for two CPU-checked next-stage routines.
// @category Restoration
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.security.MessageDigest;
import java.io.PrintWriter;
import java.util.*;
import com.google.gson.GsonBuilder;

public class AnnotateBiwnArithmetic extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=1) throw new IllegalArgumentException("Supply annotation report JSON path");
        byte[] image=new byte[0xfc000];
        if(currentProgram.getMemory().getBytes(toAddr(0x4000),image)!=image.length)
            throw new IllegalArgumentException("Candidate image is not fully mapped");
        String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image));
        if(!hash.equals("52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453"))
            throw new IllegalArgumentException("Candidate image hash differs");
        FunctionManager manager=currentProgram.getFunctionManager();
        boolean splitRemoved=manager.getFunctionAt(toAddr(0xd1ec))!=null;
        if(splitRemoved) manager.removeFunction(toAddr(0xd1ec));
        Function helper=manager.getFunctionAt(toAddr(0xd1e0));
        if(helper==null) throw new IllegalStateException("Division helper was not found");
        helper.setBody(new AddressSet(toAddr(0xd1e0),toAddr(0xd205)));
        helper.setName("analyst_u32_div_u16",SourceType.USER_DEFINED);
        DataType u32=UnsignedIntegerDataType.dataType;
        DataType u16=UnsignedShortDataType.dataType;
        helper.updateFunction(null,new ReturnParameterImpl(u32,currentProgram.getRegister("D1"),currentProgram),
            Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.USER_DEFINED,
            new ParameterImpl("divisor",u16,currentProgram.getRegister("D0w"),currentProgram),
            new ParameterImpl("numerator",u32,currentProgram.getRegister("D1"),currentProgram));
        helper.setComment("Analyst-assigned name and register signature. Original nonzero-divisor CPU routine checked against 296 fixtures. D2 preserved. Zero-divisor trap and full flags ABI excluded. Upstream DIVU semantics are unsuitable; use the separate candidate language or reviewed portable C.");
        Function position=manager.getFunctionAt(toAddr(0xd206));
        if(position==null) throw new IllegalStateException("CD offset routine was not found");
        position.setName("analyst_cd_offset_msf",SourceType.USER_DEFINED);
        position.updateFunction(null,new ReturnParameterImpl(u32,currentProgram.getRegister("D0"),currentProgram),
            Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.USER_DEFINED,
            new ParameterImpl("selector",u32,4,currentProgram),
            new ParameterImpl("byte_offset",u32,8,currentProgram));
        position.setComment("Analyst-assigned name and local signature from actual stack reads and CPU fixtures. Selector is adjusted while scanning zero-session entries; it is not an unconditional track number. 174 supplied-TOC fixtures checked. Actual BIOS TOC and CD execution unverified.");
        Map<String,Object> report=new LinkedHashMap<>();
        report.put("candidate_sha256",hash);
        report.put("language",currentProgram.getLanguageID().toString());
        report.put("removed_split_entry_d1ec",splitRemoved);
        List<Map<String,Object>> signatures=new ArrayList<>();
        for(Function function:new Function[]{helper,position}) {
            Map<String,Object> row=new LinkedHashMap<>();
            row.put("entry",function.getEntryPoint().toString());row.put("name",function.getName());
            row.put("signature",function.getSignature().toString());
            row.put("return_storage",function.getReturn().getVariableStorage().toString());
            List<String> params=new ArrayList<>();
            for(Parameter parameter:function.getParameters())params.add(parameter.getName()+":"+parameter.getVariableStorage());
            row.put("parameters",params);signatures.add(row);
        }
        report.put("signatures",signatures);
        report.put("scope","Local analyst annotations from selected CPU fixtures; original names/compiler ABI/whole-game behavior not established.");
        try(PrintWriter output=new PrintWriter(args[0])) {
            new GsonBuilder().setPrettyPrinting().create().toJson(report,output);
        }
    }
}
