#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(void){
 char python[PATH_MAX],script[PATH_MAX],log[PATH_MAX];const char *user_directory=getenv("HOME");if(!user_directory)return 2;
 if(snprintf(python,sizeof(python),"%s/.lmstudio/local-ai-lab/.venv/bin/python3.12",user_directory)>=(int)sizeof(python)||snprintf(script,sizeof(script),"%s/.lmstudio/local-ai-lab/native-preview-v1/scripts/run_biwn_native_keyboard_v1.py",user_directory)>=(int)sizeof(script)||snprintf(log,sizeof(log),"%s/.lmstudio/local-ai-lab/native-preview-v1/runs/launcher.log",user_directory)>=(int)sizeof(log))return 3;
 if(!freopen(log,"a",stdout)||!freopen(log,"a",stderr))return 4;
 execl(python,python,"-u",script,"--play-audio",(char*)NULL);perror("Native BIWN launch");return 127;
}
