#include <mach-o/dyld.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(void){
 char executable[PATH_MAX],root[PATH_MAX],python[PATH_MAX],script[PATH_MAX],log[PATH_MAX];uint32_t size=sizeof(executable);
 if(_NSGetExecutablePath(executable,&size)||!realpath(executable,root))return 2;
 for(unsigned i=0;i<4;i++){char *slash=strrchr(root,'/');if(!slash)return 3;*slash=0;}
 if(snprintf(python,sizeof(python),"%s/.venv/bin/python3.12",root)>=(int)sizeof(python)||snprintf(script,sizeof(script),"%s/scripts/run_biwn_native_keyboard_v1.py",root)>=(int)sizeof(script)||snprintf(log,sizeof(log),"%s/runs/native-preview-launcher.log",root)>=(int)sizeof(log))return 4;
 if(!freopen(log,"a",stdout)||!freopen(log,"a",stderr))return 5;
 execl(python,"python3.12","-u",script,"--play-audio",(char*)NULL);perror("Native BIWN launch");return 127;
}
