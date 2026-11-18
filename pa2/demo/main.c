#include <am.h>
#include <klib.h>
int main(void){
  char text[96],small[4];
  assert(sprintf(text,"%s %d %u %08x %%", "RV32IM",(int)0x80000000u,0xffffffffu,0x1234u)==40);
  assert(strcmp(text,"RV32IM -2147483648 4294967295 00001234 %")==0);
  assert(snprintf(small,sizeof(small),"%d",12345)==5);
  assert(strcmp(small,"123")==0);
  strcpy(text,"abcdef");memmove(text+1,text,6);assert(memcmp(text,"aabcdef",7)==0);
  memmove(text,text+1,6);text[6]=0;assert(strcmp(text,"abcdef")==0);
  strncpy(small,"x",4);assert(small[0]=='x' && small[1]==0 && small[3]==0);
  assert(strncmp("abc","abd",2)==0);assert(strcmp("\xff","\x01")>0);
  volatile int n=100;int sum=0;for(int i=1;i<=n;++i)sum+=i;
  assert(sum==5050);printf("Week14 AM: sum=%d; strings/format PASS\n",sum);
  return 0;
}
