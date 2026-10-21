"""Restricted C candidate gate; isolate pointers and bind explicit source provenance."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from pycparser import c_ast, c_parser
import check_biwn_native_format_string as gate


def validate_c(source):
    if not source.strip() or len(source.encode()) > 32000:
        raise ValueError('Complete C required, maximum32000UTF8bytes')
    clean = re.sub(r'''("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(/\*[\s\S]*?\*/|//[^\n]*)''',
                   lambda m: m[1] or ' ', source)
    if '\\\n' in clean or '%:' in clean or '??' in clean:
        raise ValueError('Preprocessor continuations/digraphs/trigraphs unsupported')
    lines = []
    for line in clean.splitlines():
        if line.lstrip().startswith('#'):
            if not re.fullmatch(r'\s*#\s*include\s+(?:"(?:format-string-native|m68k-fact-helpers-v2)\.h"|<stdint\.h>)\s*', line):
                raise ValueError('Only the supplied ABI/ISA headers and stdint.h allowed')
        else:
            lines.append(line)
    prelude = 'typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;typedef unsigned long long uint64_t;typedef signed char int8_t;typedef short int16_t;typedef int int32_t;typedef unsigned int uintptr_t;'
    tree = c_parser.CParser().parse(prelude+'\n'+'\n'.join(lines))
    functions = [node for node in tree.ext if isinstance(node, c_ast.FuncDef)]
    names = {node.decl.name for node in functions}
    target = 'biwn_native_format_string_body'
    if target not in names or any(node.decl.name != target and 'static' not in node.decl.storage for node in functions):
        raise ValueError('Define the target function; all other functions must be static')
    if any(isinstance(node, c_ast.Decl) for node in tree.ext):
        raise ValueError('File-scope objects/external function declarations unsupported')
    allowed = names | {'PR8','PR16','PR32','PW8','PW16','PW32','mf_word','mf_logic',
                       'mf_sub16','mf_add16','mf_move16','mf_move32','mf_sub_word',
                       'mf_add_word','mf_gt','mf_le','mf_cmp32'}
    class Check(c_ast.NodeVisitor):
        def visit_FuncCall(self,node):
            if not isinstance(node.name,c_ast.ID) or node.name.name not in allowed:
                raise ValueError('Only static functions and supplied ISA/memory helpers allowed')
            self.generic_visit(node)
        def visit_ArrayDecl(self,node):
            raise ValueError('No declared arrays or embedded machine-code data')
        def visit_Constant(self,node):
            if node.type=='string': raise ValueError('No string/assembler payloads')
        def visit_PtrDecl(self,node):
            if isinstance(node.type,c_ast.FuncDecl): raise ValueError('No function pointers')
            self.generic_visit(node)
    Check().visit(tree)
    return dict(functions=sorted(names),strict_preprocessing=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('receipt',type=Path)
    parser.add_argument('--author-receipt',type=Path)
    parser.add_argument('--mutation-control',action='store_true')
    parser.add_argument('--limit',type=int)
    args=parser.parse_args();source=args.source.resolve();receipt=args.receipt.resolve()
    receipt.mkdir(parents=True,exist_ok=True)
    provenance=dict(source_origin='external_candidate',local_model_authored_C=None)
    if args.author_receipt:
        author=json.loads(args.author_receipt.read_text())
        assert Path(author['source']).resolve()==source and author['source_sha256']==gate.sha(source)
        assert author['status']=='terminal_local_Author_candidate_unverified'
        provenance=dict(source_origin='local_LM_Studio_Author',local_model_authored_C=True,
                        Author_receipt=str(args.author_receipt.resolve()),Author_receipt_sha256=gate.sha(args.author_receipt))
    if args.mutation_control:
        assert not args.author_receipt
        provenance=dict(source_origin='coordinator_deliberate_negative_control',local_model_authored_C=False)
    ast=validate_c(source.read_text())
    gate.save(receipt/'source-validation.json',dict(source=str(source),sha256=gate.sha(source),AST=ast,**provenance))
    actual_save=gate.save
    def isolated_save(path,value):
        path=Path(path)
        if isinstance(value,dict) and value.get('source')==str(source):value=dict(value,**provenance)
        if path.parent==gate.ROOT/'verification':path=receipt/path.name
        actual_save(path,value)
    gate.save=isolated_save
    sys.argv=[gate.__file__,'--source',str(source)]+(['--limit',str(args.limit)]if args.limit else[])
    gate.main()


if __name__=='__main__':main()
