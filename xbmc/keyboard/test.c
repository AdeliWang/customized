#include <unistd.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/select.h>
#include <termios.h>
#include <stropts.h>
#include <stdbool.h>

#include <sys/time.h> /* struct timeval, select() */
/* ICANON, ECHO, TCSANOW, struct termios */
#include <stdlib.h> /* atexit(), exit() */

int _kbhit()
{
    static const int STDIN = 0;
    static bool initialized = false;
    if (! initialized)
    {
        // Use termios to turn off line buffering
        struct termios term;
        tcgetattr(STDIN, &term);
        term.c_lflag &= ~ICANON;
        tcsetattr(STDIN, TCSANOW, &term);
        setbuf(stdin, NULL);
        initialized = true;
    }
    int bytesWaiting;
    ioctl(STDIN, FIONREAD, &bytesWaiting);
    return bytesWaiting;
}

int kbhit(void)
{
    struct timeval tv;
    fd_set read_fd;

    tv.tv_sec=0;
    tv.tv_usec=0;
    FD_ZERO(&read_fd);
    FD_SET(0,&read_fd);

    if(select(1, &read_fd, NULL, NULL, &tv) == -1)
        return 0;

    if(FD_ISSET(0,&read_fd))
        return 1;
    printf("ddfd\n");
    return 0;
}

int wFile()
{  
    FILE *fh;  
    fh = fopen("/tmp/log", "w+");  
    fprintf(fh, "hello world!");  
    fclose(fh);  
    return 0;  
}  

int main (int argc, char *argv[])
{
    int ret;
    printf("-----\n");
    ret = kbhit();
    printf("ret=%d\n", ret);
    exit(0);
}

int main2(int argc, char** argv)
{
    printf("Press any key");
    while ( _kbhit())
    {
        printf(".");
        fflush(stdout);
        wFile(); 
        usleep(1000);
    }
    printf("\nDone.\n");
    return 0;
}
