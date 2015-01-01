//com.app

/*
 * ICom.cpp
 *
 *  Created on: 2013-4-2
 *      Author: 高辉力
 */

#include "ICom.h"

namespace std {

    /************************************
      功能：构造函数

      参数：无

      返回值：无
     ***********************************/
    ICom::ICom() {
        this->fd = 0;
        this->epid = epoll_create(6);
    }

    /************************************
      功能：根据端口号打开对应的com口,并创建数据接受线程

      参数：const int Com_port 端口号

      返回值： 0：则失败，否则返回1
     ***********************************/
    bool ICom::OpenCom(const int Com_port) {
        bool result = false;
        char pathname[20];

        if ((Com_port < 0) || (Com_port > 6)) //判断Com_port是否越界。
        {
            printf("the port is out range");
            return result;
        }

        sprintf(pathname, "/dev/ttyS%d", Com_port);

        if (fd != 0) { //判断文件__detachstate是否被占用。
            printf("com is busying!\n");
            return result;
        }

        fd = open(pathname, O_RDWR | O_NOCTTY | O_NDELAY);

        if (fd < 0) //如果文件操作符小于0表示打开文件失败。
        {
            printf("Can‘t open serial port");
            return result;
        }
        if (isatty(fd) == 0) //判断文件操作符所代表的文件是否为非终端。
        {
            printf("isatty is not a terminal device");
            return result;
        }
        //下面开始创建接受线程。
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        // 设置线程绑定属性
        int res = pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM);
        // 设置线程分离属性
        res += pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
        //创建线程
        pthread_create(&pid, &attr, ReadThreadFunction, (void *) this);
        result = true;
        return result;
    }

    /************************************
      功能：配置com口

      参数：const int Baud_rate 波特率，const int Data_bits 数据位 ， char Parity 校验位,const int Stop_bits 停止位

      返回值： 0：则失败，否则返回1
     ***********************************/
    bool ICom::SetCom(const int Baud_rate, const int Data_bits, char Parity,
            const int Stop_bits) {
        bool result = false;
        struct termios newtio;

        bzero(&newtio, sizeof(newtio));

        newtio.c_cflag |= CLOCAL | CREAD;
        newtio.c_cflag &= ~CSIZE;

        //设置波特率。
        switch (Baud_rate) {
            case 2400:
                cfsetispeed(&newtio, B2400);
                cfsetospeed(&newtio, B2400);
                break;
            case 4800:
                cfsetispeed(&newtio, B4800);
                cfsetospeed(&newtio, B4800);
                break;
            case 9600:
                cfsetispeed(&newtio, B9600);
                cfsetospeed(&newtio, B9600);
                break;
            case 19200:
                cfsetispeed(&newtio, B19200);
                cfsetospeed(&newtio, B19200);
                break;
            case 38400:
                cfsetispeed(&newtio, B38400);
                cfsetospeed(&newtio, B38400);
                break;
            default:
            case 115200:
                cfsetispeed(&newtio, B115200);
                cfsetospeed(&newtio, B115200);
                break;
        }

        //设置数据位，只支持7，8
        switch (Data_bits) {
            case 7:
                newtio.c_cflag |= CS7;
                break;
            case 8:
                newtio.c_cflag |= CS8;
                break;
            default:
                printf("Unsupported Data_bits\n");
                return result;
        }

        //设置校验位
        switch (Parity) {
            default:
            case 'N':
            case 'n': {
                          newtio.c_cflag &= ~PARENB;
                          newtio.c_iflag &= ~INPCK;
                      }
                      break;
            case 'o':
            case 'O': {
                          newtio.c_cflag |= (PARODD | PARENB);
                          newtio.c_iflag |= INPCK;
                      }
                      break;
            case 'e':
            case 'E': {
                          newtio.c_cflag |= PARENB;
                          newtio.c_cflag &= ~PARODD;
                          newtio.c_iflag |= INPCK;
                      }
                      break;

            case 's':
            case 'S': {
                          newtio.c_cflag &= ~PARENB;
                          newtio.c_cflag &= ~CSTOPB;
                      }
                      break;
        }
        //设置停止位，值为1 or 2
        switch (Stop_bits) {
            case 1: {
                        newtio.c_cflag &= ~CSTOPB;
                        break;
                    }
            case 2: {
                        newtio.c_cflag |= CSTOPB;
                        break;
                    }
            default:
                    printf("Unsupported Stop_bits.\n");
                    return result;

        }
        //设置最少字符和等待时间，对于接收字符和等待时间没有特别的要求时，可设为0：
        newtio.c_cc[VTIME] = 0;
        newtio.c_cc[VMIN] = 0;

        //刷清输入和输出队列
        tcflush(0, TCIOFLUSH);

        //激活配置，TCSANOW表示更改后立即生效。
        if ((tcsetattr(fd, TCSANOW, &newtio)) != 0) { //判断是否激活成功。
            printf("Com set error\n");
            return result;
        }
        result = true;
        return result;
    }
    /************************************
      功能：数据接收线程的函数

      参数：对象指针

      返回值： 无
     ***********************************/
    void * ICom::ReadThreadFunction(void *arg) {
        printf("------------start ReadThread--------------\n");

        ICom *com = (ICom*) arg;

        //epoll设置
        com->event.data.fd = com->fd;
        com->event.events = EPOLLET | EPOLLIN;
        if (epoll_ctl(com->epid, EPOLL_CTL_ADD, com->fd, &com->event) != 0) { //将读事件添加到epoll的事件队列中
            printf("set epoll error!\n");
            return NULL;
        }
        printf("------------set epoll ok!-----------------\n");

        //下面开始epoll等待
        int i = 0, waiteNum = 0;
        while (true) {
            waiteNum = epoll_wait(com->epid, com->events, 0, 0);
            for (i = 0; i < waiteNum; i++) {
                if (com->events[i].events & EPOLLIN) { //判断是否有数据进入
                    //接受数据
                    com->ComRead(com->RecvBuff, MAXLEN);
                    //数据处理
                    com->ReadDataProc(com->RecvBuff, MAXLEN);
                }
            }
        }
        return NULL;
    }
    /************************************
      功能：数据处理的虚函数，可以在子类中实现

      参数：char * DataBuff 存储数据指针, const int BuffLen 数据长度

      返回值： 无
     ***********************************/
    void ICom::ReadDataProc(char * DataBuff, const int BuffLen) {

        printf("I am ReadDataProc!\n");
        printf("RecvData is %s\n", DataBuff);
    }

    /************************************
      功能：Com口读数据

      参数：char * ReadBuff 存储读出的数据，const int ReadLen 读出的长度

      返回值：实际读取长度，-1表示读取失败
     ***********************************/
    int ICom::ComRead(char * ReadBuff, const int ReadLen) {
        if (fd < 0) { //判断操作符是否打开
            printf("Com error!\n");
            return -1;
        }
        int len = 0;
        int rdlen = 0;
        while (true) {
            rdlen = read(fd, ReadBuff + len, ReadLen);
            len += rdlen;
            if (len == ReadLen) {
                return len;
            }
        }
        return len;
    }
    /************************************
      功能：Com口读数据

      参数：char * WriteBuff 写入的数据，const int ReadLen 写入的长度

      返回值：写入长度,-1表示写入失败
     ***********************************/
    int ICom::ComWrite(char *WriteBuff, const int WriteLen) {
        if (fd < 0) { //判断操作符是否打开
            printf("Com error!\n");
            return -1;
        }
        int wlen = write(fd, WriteBuff, WriteLen);
        return wlen;
    }

    /************************************
      功能：Com关闭

      参数：无

      返回值：无
     ***********************************/
    void ICom::ComClose() {
        if (this->fd > 0) { //判断文件描述符是否存在
            close(this->fd);
        }
    }

    /************************************
      功能：析构函数

      参数：无

      返回值：无
     ***********************************/
    ICom::~ICom() {
        ComClose();
    }

} /* namespace std */

