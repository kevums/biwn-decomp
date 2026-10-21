#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(int argc,char **argv){
 char python[PATH_MAX],script[PATH_MAX],log[PATH_MAX];const char *user_directory=getenv("HOME");if(!user_directory)return 2;
 if(snprintf(python,sizeof(python),"%s/.lmstudio/local-ai-lab/.venv/bin/python3.12",user_directory)>=(int)sizeof(python)||snprintf(script,sizeof(script),"%s/.lmstudio/local-ai-lab/native-preview-v3/scripts/run_biwn_native_keyboard_v3.py",user_directory)>=(int)sizeof(script)||snprintf(log,sizeof(log),"%s/.lmstudio/local-ai-lab/native-preview-v3/runs/launcher.log",user_directory)>=(int)sizeof(log))return 3;
 if(!freopen(log,"a",stdout)||!freopen(log,"a",stderr))return 4;
 if(chdir("/"))return 5;
 char **args=calloc((size_t)argc+5,sizeof(char *));if(!args)return 6;
 unsigned n=0;args[n++]=python;args[n++]="-u";args[n++]=script;args[n++]="--play-audio";
 for(int i=1;i<argc;i++)if(strncmp(argv[i],"-psn_",5))args[n++]=argv[i];
 args[n]=NULL;execv(python,args);perror("BIWN test preview launch");return 127;
}
