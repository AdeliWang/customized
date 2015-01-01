#ifndef _SERIAL_H_H_14_09_01_
#define _SERIAL_H_H_14_09_01_


#include "unistd.h"
#include "sys/types.h"
#include "sys/stat.h"
#include "fcntl.h"
#include
#include "errno.h"
#include "string.h"
#include
#include "sys/time.h"
#include "sys/epoll.h"

class CSerial {
public:
enum
{
MAXLEN=1024
};
CSerial();
virtual ~CSerial();

bool Open(const char* uartPort);//根据端口号打开串口，并创建接收线程
bool SetConfig(const int& iBaudRate, const int& iDataBits,const char& cParity, const int& iStopBits);//设置串口
int Write(const unsigned char *pWriteBuff, const int &iWriteLen);//串口写数据
int Read(unsigned char* o_pReadBuff, const int& iReadLen);//串口读数据
void Close();//关闭com口
protected:
static void * ReadThreadFunction(void * o_pArg);//接受数据的线程函数
virtual void ReadDataProc()=0;//数据的处理函数
private:

int m_iFd;//文件描述符
int m_iEpid; //epoll标识符
epoll_event m_event;
epoll_event m_events[6];//事件集合
pthread_t m_pid;//接受数据线程的Id
};

#endif
