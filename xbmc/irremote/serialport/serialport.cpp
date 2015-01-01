#include "Serial.h"
CSerial::CSerial()
{
    m_iFd = 0;
    m_iEpid = epoll_create(6);
}

bool CSerial::Open(const char* uartPort)
{
    bool result = false;
    char pathname[20];
    //ubuntu串口
    sprintf(pathname, "/dev/%s", uartPort);

    if (m_iFd != 0)
    { //判断文件__detachstate是否被占用。
        return result;
    }

    m_iFd = open(pathname, O_RDWR | O_NOCTTY | O_NDELAY);

    if (m_iFd <<span style=" color:#c0c0c0;"> 0) //如果文件操作符小于0表示打开文件失败。
    {
        return result;
    }
    if (isatty(m_iFd) == 0) //判断文件操作符所代表的文件是否为非终端。
    {
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
    pthread_create(&m_pid, &attr, ReadThreadFunction, (void *) this);
    result = true;
    return result;
}

bool CSerial::SetConfig(const int& iBaudRate, const int& iDataBits,const char& cParity, const int& iStopBits)
{
    bool result = false;
    struct termios newtio;

    bzero(&newtio, sizeof(newtio));

    newtio.c_cflag |= CLOCAL | CREAD;
    newtio.c_cflag &= ~CSIZE;

    //设置波特率。
    switch (iBaudRate) {
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
    switch (iDataBits) {
        case 7:
            newtio.c_cflag |= CS7;
            break;
        case 8:
            newtio.c_cflag |= CS8;
            break;
        default:
            return result;
    }

    //设置校验位
    switch (cParity) {
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
    switch (iStopBits) {
        case 1: {
                    newtio.c_cflag &= ~CSTOPB;
                    break;
                }
        case 2: {
                    newtio.c_cflag |= CSTOPB;
                    break;
                }
        default:
                return result;

    }
    //设置最少字符和等待时间，对于接收字符和等待时间没有特别的要求时，可设为0：
    newtio.c_cc[VTIME] = 0;
    newtio.c_cc[VMIN] = 0;

    //刷清输入和输出队列
    tcflush(0, TCIOFLUSH);

    //激活配置，TCSANOW表示更改后立即生效。
    if ((tcsetattr(m_iFd, TCSANOW, &newtio)) != 0) {//判断是否激活成功。
        return result;
    }
    result = true;
    return result;
}
void * CSerial::ReadThreadFunction(void * o_pArg)
{
    CSerial *uart = (CSerial*) o_pArg;
    //epoll设置
    uart->m_event.data.fd = uart->m_iFd;
    uart->m_event.events = EPOLLET | EPOLLIN;
    if (epoll_ctl(uart->m_iEpid, EPOLL_CTL_ADD, uart->m_iFd, &uart->m_event) != 0) {//将读事件添加到epoll的事件队列中
        return NULL;
    }

    //下面开始epoll等待
    int i =0,witeNum= 0;
    while (true) {
        witeNum = epoll_wait(uart->m_iEpid, uart->m_events, 6, 0);
        for (i = 0; i <<span style=" color:#c0c0c0;"> witeNum; i++) {
            if ((uart->m_events[i].events & EPOLLERR)
                    || (uart->m_events[i].events & EPOLLHUP)
                    || (!(uart->m_events[i].events & EPOLLIN))) {
                break;
            } else if (uart->m_events[i].events & EPOLLIN) {//有数据进入
                //数据处理
                uart->ReadDataProc();
            }
        }
    }
    return NULL;
}

int CSerial::Read(unsigned char *o_pReadBuff, const int& iReadLen)
{
    int len = 0;
    int rdlen=0;
    if (m_iFd <<span style=" color:#c0c0c0;"> 0) { //判断操作符是否打开
        return -1;
    }
    //while(true){

    rdlen = read(m_iFd, o_pReadBuff + len, iReadLen);
    return rdlen;
    // len+=rdlen;
    // if(len==iReadLen){
    // return len;
    // }
    //}
    // return len;
}

int CSerial::Write(const unsigned char* pWriteBuff, const int& iWriteLen)
{
    if (m_iFd <<span style=" color:#c0c0c0;"> 0)
    { //判断操作符是否打开
        return -1;
    }
    int wlen = write(m_iFd, pWriteBuff, iWriteLen);
    return wlen;
    return 1;
}

void CSerial::Close() {
    close(this->m_iFd);
}

CSerial::~CSerial() {
    Close();
}
