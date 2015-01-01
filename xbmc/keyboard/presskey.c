#include <unistd.h>
#include <fcntl.h>
#include <sys/select.h>
#include <stdio.h>
#include <stdlib.h>
void settermios(int flag)
{
    if(flag)
        system("stty cbreak -echo");
    else
        system("stty cooked echo");
}
int kbhit(void)
{
    struct timeval tv;
    fd_set rdfs;
    tv.tv_sec = 0;
    tv.tv_usec = 0;
    FD_ZERO(&rdfs);
    FD_SET (STDIN_FILENO, &rdfs);
    select(STDIN_FILENO+1, &rdfs, NULL, NULL, &tv);
    return FD_ISSET(STDIN_FILENO, &rdfs);
}
int main()
{
    settermios(1);
    while(!kbhit()){
        printf("No keys are pressed\n");
        sleep(1);
    }
    printf("You pressed:%c \n",getchar());
    settermios(0);
    return 0;
}
