"""Bounded interpreter for the recorded91C510 instruction subset,not a PE runner."""
import re,struct
class CtorOracleError(ValueError):pass
def number(value):
    value=value.strip()
    return int(value[:-1],16) if value.lower().endswith('h') else int(value,0)
def interpret(instructions,read_constant):
    base=0x10000000;data=bytearray(b'\xa5'*1188);regs={key:0 for key in ['eax','ebx','ecx','esi','edi','esp']};regs['ecx']=base;regs['esp']=0x20000000;stack={};fp=[]
    def load(value):
        if value=='bl':return regs['ebx']&255
        return regs[value] if value in regs else number(value)
    def address(operand):
        expression=re.search(r'\[([^]]+)\]',operand)
        if not expression:raise CtorOracleError('No memory operand:'+operand)
        terms=expression[1].split('+');result=regs[terms.pop(0)]
        for term in terms:result+=-int(term[4:],16) if term.startswith('var_') else number(term)
        return result
    def write(at,value,size=4):
        if base<=at and at+size<=base+len(data):data[at-base:at-base+size]=int(value&((1<<(size*8))-1)).to_bytes(size,'little')
        elif 0x1ffff000<=at<0x20000000 and size==4:stack[at]=value&0xffffffff
        else:raise CtorOracleError('Write outside owned object/argument stack')
    def push(value):regs['esp']-=4;stack[regs['esp']]=value
    def pop():
        try:value=stack.pop(regs['esp'])
        except KeyError as error:raise CtorOracleError('Invalid stack pop') from error
        regs['esp']+=4;return value
    returned=False
    for line in instructions:
        if returned:raise CtorOracleError('Instruction after constructor return')
        text=line.split(';',1)[0].strip();op,_,tail=text.partition(' ');args=[x.strip() for x in tail.split(',')]
        if op=='push':push(load(args[0]))
        elif op=='pop':regs[args[0]]=pop()
        elif op=='xor' and args[0]==args[1]:regs[args[0]]=0
        elif op=='mov':
            if '[' in args[0]:write(address(args[0]),load(args[1]),1 if args[1]=='bl' or args[0].startswith('byte ptr') else 4)
            else:regs[args[0]]=load(args[1])
        elif op=='lea':regs[args[0]]=address(args[1])
        elif op=='add' and args[0]=='esp':
            amount=number(args[1])
            if amount%4:raise CtorOracleError('Unaligned argument cleanup')
            for _ in range(amount//4):pop()
        elif op=='fldz':fp.insert(0,0)
        elif op=='fld1':fp.insert(0,0x3f800000)
        elif op=='fld' and args[0].startswith('ds:flt_'):fp.insert(0,read_constant(int(args[0][7:],16)))
        elif op=='fxch':
            index=int(re.fullmatch(r'st\((\d+)\)',args[0])[1])
            if len(fp)<=index:raise CtorOracleError('FP stack underflow')
            fp[0],fp[index]=fp[index],fp[0]
        elif op in ['fst','fstp']:
            if not fp:raise CtorOracleError('FP stack underflow')
            write(address(tail),fp[0])
            if op=='fstp':fp.pop(0)
        elif op=='call':
            sp=regs['esp']
            if tail=='_memset':
                at,value,size=[stack[sp+4*i] for i in range(3)]
                if at!=base or value or size!=1188:raise CtorOracleError('Unexpected constructor memset')
                data[:]=bytes(1188);regs['eax']=base
            elif tail=='sub_91C450':
                at=stack[sp]
                if at!=base+720:raise CtorOracleError('Unexpected material helper target')
                data[720:788]=bytes(68)
                for i in range(4):
                    value=stack[sp+4*(i+1)];write(at+4*i,value);write(at+16+4*i,value)
                regs['eax']=at
            else:raise CtorOracleError('Unrecognized constructor call:'+tail)
        elif op=='retn':
            if fp or regs['esp']!=0x20000000 or regs['eax']!=base:raise CtorOracleError('Unbalanced constructor state')
            returned=True
        else:raise CtorOracleError('Unsupported constructor instruction:'+text)
    if not returned:raise CtorOracleError('Missing constructor return')
    return bytes(data)
