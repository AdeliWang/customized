
#include "serial.h"
#include <map>
#include <algorithm>
 
CSerial::CSerial(const string & dev): fd(-1),dev(dev)
{
}

CSerial::~CSerial()
{
    if ( isopen() )
        close();
}

int CSerial::open()
{
    if( isopen() )
        return fd;
    /*
    O_RDONLY, O_WRONLY, O_RDWR 
    O_NOCTTY  // terminal mode
    O_NONBLOCK :unblock mode; O_NDELAY :block mode
    */
    fd=::open(dev.c_str(), O_RDWR|O_NOCTTY|O_NDELAY);
    if (fd == -1)
    {
        ::perror("open failed");
        return fd;
    }
    flush();
    return fd;
}

bool CSerial::close()
{
    if ((fd == -1) || (::close( fd ) == -1 ))
    {
        ::perror("close failed");
        fd = -1;
        return false;
    }
    fd = -1;
    return true;
}

bool CSerial::flush()
{
    if ( ::tcflush( fd , TCIFLUSH ) == -1 )
    {
        ::perror( "tcflush failed" );
        return false;
    }
    return true;
}

bool CSerial::set_speed( int baudrate )
{
    if (isopen() == false) return false;

    const map<int, int>::value_type init_value[] =
                                        {
                                            map<int, int>::value_type(115200, B115200),
                                            map<int, int>::value_type(57600, B57600),
                                            map<int, int>::value_type(38400, B38400),
                                            map<int, int>::value_type(19200, B19200),
                                            map<int, int>::value_type(4800,  B4800),
                                            map<int, int>::value_type(2400,  B2400),
                                            map<int, int>::value_type(1200,  B1200),
                                            map<int, int>::value_type(300,   B300)
                                        };
    map<int, int> map_speed(init_value, init_value + 8);

    std::map<int, int>::iterator it;
    it = map_speed.find(baudrate);
    int speed = 0;
    if (it != map_speed.end())
        return false;
    else
        speed = it->second;

    struct termios   opt;
    tcgetattr(fd, &opt);
    tcflush(fd, TCIOFLUSH);
    cfsetispeed(&opt, speed);
    cfsetospeed(&opt, speed);
    int status = tcsetattr(fd, TCSANOW, &opt);
    return (status == 0);
}

bool CSerial::set_ctrl(int databits, int stopbits, int parity)
{
    if (isopen() == false) return false;

    struct termios options;
    int result = tcgetattr(fd,&options);
    if(result != 0)
    {
        return false;
    }

    /*8N1*/
    options.c_cflag &= ~CSIZE; /* Mask the character size bits */
    switch (databits)
    {
        case 7:
            options.c_cflag |= CS7;
            break;
        case 8:
            options.c_cflag |= CS8;
            break;
        default:
            throw 11;
            break;
    }

    switch (parity)
    {
        case 'n':
        case 'N':
            options.c_cflag &= ~PARENB;   /* Clear parity enable */
            options.c_iflag &= ~INPCK;     /* Enable parity checking */
            break;
        case 'o':
        case 'O':
            options.c_cflag |= (PARODD | PARENB);  /* Set odd checking*/
            options.c_iflag |= INPCK;             /* Disnable parity checking */
            break;
        case 'e':
        case 'E':
            options.c_cflag |= PARENB;     /* Enable parity */
            options.c_cflag &= ~PARODD;   /* Set event checking*/ 
            options.c_iflag |= INPCK;       /* Disnable parity checking */
            break;
        case 'S':
        case 's':  /*as no parity*/
            options.c_cflag &= ~PARENB;
            options.c_cflag &= ~CSTOPB;
            break;
        default:
            throw 12;
            break;
    }

    //set stop bits
    switch (stopbits)
    {
        case 1:
            options.c_cflag &= ~CSTOPB;
            break;
        case 2:
            options.c_cflag |= CSTOPB;
            break;
        default:
            throw 13;
            break;
    }

    /* Set input parity option */
    if (parity != 'n') {
        options.c_iflag |= INPCK;
    }

    //options.c_cc[VTIME] = 150; // 15 seconds
    //options.c_cc[VMIN] = 0;    // effective on block mode; block to read until 0 character arrives 

    options.c_cflag &= ~CRTSCTS;//disable hardware flow control;
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);/*raw input*/
    options.c_oflag  &= ~OPOST;   /*raw output*/

    tcflush(fd,TCIFLUSH); /* Update the options and do it NOW */
    result = tcsetattr(fd,TCSANOW,&options);
    return (result == 0);
}

bool CSerial::set_mode(const char mode, int tmout, int vmin)
{
    if (isopen() == false) return false;

    bool res = false;
    if (mode == 'n') // nonblock
        res = (fcntl(fd, F_SETFL, FNDELAY) >= 0);
    else if (mode == 'b')// block
        res = (fcntl(fd, F_SETFL, 0) >= 0);
    else
        throw 21;

    if (false == res) return false;

    struct termios options;
    res = tcgetattr(fd,&options);
    if(res != 0)   return false;

    options.c_cflag &= ~CSIZE; /* Mask the character size bits */
    options.c_cc[VTIME] = tmout * 10; // TIME *0.1 s
    options.c_cc[VMIN] = vmin;    // effective on block mode; block to read until 0 character arrives 
    tcflush(fd,TCIFLUSH); /* Update the options and do it NOW */
    res = tcsetattr(fd,TCSANOW,&options);
    return (res == 0);
}

int CSerial::read( char * &data, int maxsize)
{
    int size;
    if ( (size = ::read( fd, data, maxsize)) ==-1)
        ::perror( "read failed" );
    return size;
}

int CSerial::write( char * &data , int maxsize )
{
    int size;
    if ((size = ::write( fd , data , maxsize )) == -1)
        ::perror( "write failed" );
    return size;
}

#if 0
bool CSerial::set(int nSpeed, int nBits, char nEvent, int nStop)     
{     
    if (isopen() == false) return false;

    struct termios newtio;     
    struct termios oldtio;     

    if(tcgetattr(fd,&oldtio) != 0)     
    {     
        perror("SetupSerial failed");     
        return false;     
    }     

    bzero(&newtio,sizeof(newtio));     
    newtio.c_cflag |= CLOCAL |CREAD;     
    newtio.c_cflag &= ~CSIZE;     

    /**************************/      
    switch(nBits)     
    {     
        case 7:     
            newtio.c_cflag |= CS7;     
            break;     
        case 8:     
            newtio.c_cflag |= CS8;     
            break;         
    }     
    /***************************/    
    switch(nEvent)     
    {     
        case 'O':     
            newtio.c_cflag |= PARENB;     
            newtio.c_cflag |= PARODD;     
            newtio.c_iflag |= (INPCK | ISTRIP);     
            break;     
        case 'E':     
            newtio.c_iflag |= (INPCK |ISTRIP);     
            newtio.c_cflag |= PARENB;     
            newtio.c_cflag &= ~PARODD;     
            break;     
        case 'N':     
            newtio.c_cflag &= ~PARENB;     
            break;     
    }     
    /***************************/     
    switch(nSpeed)     
    {     
        case 2400:     
            cfsetispeed(&newtio,B2400);     
            cfsetospeed(&newtio,B2400);     
            break;     
        case 4800:     
            cfsetispeed(&newtio,B4800);     
            cfsetospeed(&newtio,B4800);     
            break;     
        case 9600:     
            cfsetispeed(&newtio,B9600);     
            cfsetospeed(&newtio,B9600);     
            break;   
        case 57600:     
            cfsetispeed(&newtio,B57600);     
            cfsetospeed(&newtio,B57600);     
            break;     
        case 115200:     
            cfsetispeed(&newtio,B115200);     
            cfsetospeed(&newtio,B115200);     
            break;     
        case 460800:     
            cfsetispeed(&newtio,B460800);     
            cfsetospeed(&newtio,B460800);     
            break;               
        default:     
            cfsetispeed(&newtio,B9600);     
            cfsetospeed(&newtio,B9600);     
            break;     
    }     
    /*************************/    
    if(nStop == 1){     
        newtio.c_cflag &= ~CSTOPB;     
    }     
    else if(nStop == 2){     
        newtio.c_cflag |= CSTOPB;     
    }     
    newtio.c_cc[VTIME] = 1;     
    newtio.c_cc[VMIN] = FRAME_MAXSIZE;   //effective on block mode

    tcflush(fd,TCIFLUSH);     
    if((tcsetattr(fd,TCSANOW,&newtio)) != 0)     
    {     
        perror("com set error");     
        return false;     
    }     
    return true;     
}     
#endif
// EOF
