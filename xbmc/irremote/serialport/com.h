//com.h

/*
 * ICom.h
 *
 *  Created on: 2013-4-2
 *      Author: 高辉力
 */

#ifndef ICOM_H_
#define ICOM_H_
#include "stdio.h"
#include "stdlib.h"
#include "unistd.h"
#include "sys/types.h"
#include "sys/stat.h"
#include "fcntl.h"
#include <termios.h>
#include "errno.h"
#include "string.h"
#include <pthread.h>
#include "sys/time.h"
#include "sys/epoll.h"

#define MAXLEN 1024

namespace std {

    class ICom {
        public:
            ICom();
            virtual ~ICom();

            bool OpenCom(const int Com_port);//根据端口号打开com口，并创建接收线程
            bool SetCom(const int Baud_rate, const int Data_bits, char Parity, const int Stop_bits);//设置com口

            int ComWrite(char *WriteBuff,const int WriteLen);//com口写数据
            int ComRead(char * ReadBuff,const int ReadLen);//com口读数据

            virtual void ReadDataProc(char * DataBuff,const int BuffLen);//数据的处理函数。
        private:
            int fd;//文件描述符
            int epid; //epoll标识符
            epoll_event event;
            epoll_event events[6];//事件集合
            char RecvBuff[MAXLEN];//接受到的数据
            pthread_t pid;//接受数据线程的Id
            static void * ReadThreadFunction(void * arg);//接受数据的线程函数
            void ComClose();//关闭com口

    };

} /* namespace std */
#endif /* ICOM_H_ */
