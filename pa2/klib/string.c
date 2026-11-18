#include <klib.h>
#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)
size_t strlen(const char *s){size_t n=0;while(s[n])++n;return n;}
char *strcpy(char *d,const char *s){char *r=d;while((*d++=*s++));return r;}
char *strncpy(char *d,const char *s,size_t n){size_t i=0;for(;i<n && s[i];++i)d[i]=s[i];for(;i<n;++i)d[i]=0;return d;}
char *strcat(char *d,const char *s){strcpy(d+strlen(d),s);return d;}
int strcmp(const char *a,const char *b){while(*a && *a==*b){++a;++b;}return (unsigned char)*a-(unsigned char)*b;}
int strncmp(const char *a,const char *b,size_t n){for(size_t i=0;i<n;++i){int d=(unsigned char)a[i]-(unsigned char)b[i];if(d || !a[i])return d;}return 0;}
void *memset(void *d,int c,size_t n){unsigned char *p=d;for(size_t i=0;i<n;++i)p[i]=(unsigned char)c;return d;}
void *memcpy(void *d,const void *s,size_t n){unsigned char *a=d;const unsigned char *b=s;for(size_t i=0;i<n;++i)a[i]=b[i];return d;}
void *memmove(void *d,const void *s,size_t n){unsigned char *a=d;const unsigned char *b=s;if((uintptr_t)a<(uintptr_t)b){for(size_t i=0;i<n;++i)a[i]=b[i];}else{while(n){--n;a[n]=b[n];}}return d;}
int memcmp(const void *a,const void *b,size_t n){const unsigned char *x=a,*y=b;for(size_t i=0;i<n;++i)if(x[i]!=y[i])return x[i]-y[i];return 0;}
char *strchr(const char *s,int c){for(;;++s){if(*s==(char)c)return (char *)s;if(!*s)return NULL;}}
char *strrchr(const char *s,int c){const char *r=NULL;do{if(*s==(char)c)r=s;}while(*s++);return (char *)r;}
#endif
