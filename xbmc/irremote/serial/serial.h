#ifndef _SERIAL_H_
#define _SERIAL_H_

/*
*  refer to: http://www.tldp.org/HOWTO/Serial-Programming-HOWTO/x115.html
*/

extern "C" {
#include     <stdio.h>      /*标准输入输出定义*/
#include     <stdlib.h>     /*标准函数库定义*/
#include     <unistd.h>     /*Unix 标准函数定义*/
#include     <sys/types.h>  
#include     <sys/stat.h>   
#include     <fcntl.h>      /*文件控制定义*/
#include     <termios.h>    /*PPSIX 终端控制定义*/
#include     <errno.h>      /*错误号定义*/
#include     <pthread.h>
}

#include <cstring>
#include <string>

using namespace std;

class CSerial
{
public:
    explicit CSerial(const string & dev);
	~CSerial();

	bool isopen() const {return (fd != -1);};
	int open(); 
	bool close();
	bool flush();
    bool set_speed(int baudrate);
    bool set_ctrl(int databits, int stopbits, int parity);
    bool set_mode(const char mode = 'b', int tmout = 15, int vmin=0);/*'b': block; 'n': nonblock; default: block*/
	int read( char *& , int );
	int write( char *& , int );
	
private:
    string dev;
	int fd;
};


#endif
