#ifndef _EPOLLER_H_ 
#define _EPOLLER_H_ 

class Epoller:
{
    public:
        enum Event {EV_RO=1, EV_WO, EV_WR};
        Epoller();
        ~Epoller();

        int waitEvent(std::map<Handle, EventHandler*>& handlers, int timeout = 0);
        bool regist(int fd, Event evt);
        bool remove(int fd);

    private:
        int max_fd;
        int efd;
};
#endif
