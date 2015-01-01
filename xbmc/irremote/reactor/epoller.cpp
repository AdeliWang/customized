#include <stdio.h>
#include <sys/epoll.h>
#include "epoller.h"


Epoller::Epoller()
    :max_fd(0)
{
    efd = epoll_create(1024);
}

Epoller::~Epoller()
{
    if ( efd >=0 )
        close(efd);
}

int Epoller::regist(int fd, Event evt)
{
    struct epoll_event ev;
    ev.data.fd = fd;
    if(evt & EV_RO) {
        ev.events |= EPOLLIN;
    }
    if(evt & EV_WO) {
        ev.events |= EPOLLOUT;
    }

    ev.events |= EPOLLET;

    if (0 == epoll_ctl(efd, EPOLL_CTL_ADD, fd, &ev))
    {
        ++max_fd;
        return true;
    }
    else
        return false;
}

bool Epoller::remove(int fd)
{
    struct epoll_event ev;
    if (0 != epoll_ctl(efd, EPOLL_CTL_DEL, fd, &ev))
    {
        return false;
    }

    --max_fd;
    return true;
}
int Epoller::waitEvent(std::map<fd, Eventfdr*>& fdrs, int timeout)
{
    std::vector<struct epoll_event> evs(max_fd);
    int num = epoll_wait(efd, &evs[0], max_fd, timeout);
    if(num > 0)
    {
        for(int i = 0; i < num; ++i) {
            fd fd = evs[i].data.fd;
            if(EPOLLERR & evs[i].events) {
                (fdrs[fd])->fdError();
            }
            else
            {
                if (EPOLLIN & evs[i].events) {
                    fdrs[fd]->fdRead();
                }

                if (EPOLLOUT & evs[i].events) {
                    fdrs[fd]->fdWirte();
                }
            }
        }

    }
    else if (num < 0)
    {
        printf("Hominlinx-->epollDemultiplexer::waitEvent(error[%s])\n",strerror(errno) );
    }
    return 0;
}
