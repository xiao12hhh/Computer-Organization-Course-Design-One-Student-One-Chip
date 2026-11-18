"""Compare our actual klib sources with host libc; compile with UBSan."""
import ctypes as C,random,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;b=root/'build/klib';b.mkdir(parents=True,exist_ok=True)
(b/'klib.h').write_text('#include <stdint.h>\n#include <stddef.h>\n#include <stdarg.h>\n#include <stdio.h>\n#include <string.h>\nvoid putch(char);\n')
(b/'console.c').write_text('char console[4096];unsigned position;void putch(char c){if(position<4095)console[position++]=c;}\n')
names='strlen strcpy strncpy strcat strcmp strncmp memset memmove memcpy memcmp strchr strrchr printf vprintf sprintf vsprintf snprintf vsnprintf'.split()
subprocess.run(['cc','-shared','-fPIC','-fno-builtin','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(b),*[f'-D{n}=course_{n}' for n in names],str(root/'klib/string.c'),str(root/'klib/format.c'),str(b/'console.c'),'-o',str(b/'klib.so')],check=True)
ours=C.CDLL(str(b/'klib.so'));libc=C.CDLL(None)
ptr=C.c_void_p;size=C.c_size_t
spec={'strlen':([ptr],size),'strcpy':([ptr,ptr],ptr),'strncpy':([ptr,ptr,size],ptr),'strcat':([ptr,ptr],ptr),'strcmp':([ptr,ptr],C.c_int),'strncmp':([ptr,ptr,size],C.c_int),'memset':([ptr,C.c_int,size],ptr),'memcpy':([ptr,ptr,size],ptr),'memmove':([ptr,ptr,size],ptr),'memcmp':([ptr,ptr,size],C.c_int),'strchr':([ptr,C.c_int],ptr),'strrchr':([ptr,C.c_int],ptr)}
for name,(args,result) in spec.items():
    for lib,prefix in [(ours,'course_'),(libc,'')]:f=getattr(lib,prefix+name);f.argtypes=args;f.restype=result
rng=random.Random(14);count=0
for _ in range(3000):
    raw=bytes(rng.randrange(256) for _ in range(96));a=C.create_string_buffer(raw);b2=C.create_string_buffer(raw)
    n=rng.randrange(65);src=rng.randrange(97-n);dst=rng.randrange(97-n)
    ours.course_memmove(C.addressof(a)+dst,C.addressof(a)+src,n);libc.memmove(C.addressof(b2)+dst,C.addressof(b2)+src,n)
    assert a.raw==b2.raw
    fill=rng.randrange(256);ours.course_memset(a,fill,n);libc.memset(b2,fill,n);assert a.raw==b2.raw
    other=C.create_string_buffer(bytes(rng.randrange(1,256) for _ in range(64))+b'\0')
    ours.course_memcpy(a,other,n);libc.memcpy(b2,other,n);assert a.raw==b2.raw
    ours.course_strncpy(a,other,n);libc.strncpy(b2,other,n);assert a.raw==b2.raw
    ours.course_strcpy(a,other);libc.strcpy(b2,other);assert a.raw==b2.raw
    assert ours.course_strlen(a)==libc.strlen(b2)
    for name in ['strcmp','strncmp','memcmp']:
        args=(a,other,n) if name!='strcmp' else (a,other)
        x=getattr(ours,'course_'+name)(*args);y=getattr(libc,name)(*args)
        assert (x>0)-(x<0)==(y>0)-(y<0)
    for name in ['strchr','strrchr']:
        for ch in [0,65,255]:
            x=getattr(ours,'course_'+name)(a,ch);y=getattr(libc,name)(a,ch);assert x==y
    count+=1
ours.course_snprintf.argtypes=[ptr,size,C.c_char_p];libc.snprintf.argtypes=[ptr,size,C.c_char_p]
for value in [0,1,-1,-2147483648,2147483647]+[rng.randrange(-2**31,2**31) for _ in range(1000)]:
    for fmt in [b'%d',b'%012d',b'%-14d',b'%u',b'%08x',b'%X']:
        cap=rng.randrange(24);a=C.create_string_buffer(b'Z'*32);b2=C.create_string_buffer(b'Z'*32)
        x=ours.course_snprintf(a,cap,fmt,C.c_int(value));y=libc.snprintf(b2,cap,fmt,C.c_int(value))
        assert x==y and a.raw==b2.raw,(fmt,value,cap,x,y,a.raw,b2.raw)
        count+=1
for fmt,args in [(b'%s %% %c',[C.c_char_p(b'hello'),C.c_int(65)]),(b'%8s|%-5c',[C.c_char_p(b'xy'),C.c_int(66)])]:
    for cap in range(25):
        a=C.create_string_buffer(b'Z'*32);b2=C.create_string_buffer(b'Z'*32)
        assert ours.course_snprintf(a,cap,fmt,*args)==libc.snprintf(b2,cap,fmt,*args)
        assert a.raw==b2.raw;count+=1
a=C.create_string_buffer(b'ab',20);ours.course_strcat(a,b'cd');assert a.value==b'abcd'
assert ours.course_snprintf(None,0,b'%d',C.c_int(-2147483648))==11
print('PASS klib libc oracle:',count,'cases; memory overlap, unsigned bytes, zero length, format truncation; UBSan enabled')
