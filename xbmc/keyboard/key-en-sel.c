#include<stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h> 
#include<string.h>
int b_cur_x = 0, b_cur_y = 0;

typedef enum {
    BlcTermKeyDevStat_Default               = 1, // 所有键值的默认状态或鼠标的坐标移动状态
    BlcTermKeyDevStat_Down                  = 2, // 所有键值的按下状态
    BlcTermKeyDevStat_Up                    = 3, // 所有键值的弹起状态
    BlcTermKeyDevStat_MouseWheel            = 4, // 鼠标滚轮转动   
    BlcTermKeyDevStat_ConsoleLeftAXIS   = 5, // 游戏手柄左摇杆坐标操作
    BlcTermKeyDevStat_ConsoleRightAXIS  = 6, // 游戏手柄右摇杆坐标操作
    BlcTermKeyDevStat_MouseDoubleClick  = 7, // 鼠标左键双击
}BlcTermKeyDevStat;

typedef enum {
    BlcPlayCtl_EventID_Login            = 3001,
    BlcPlayCtl_EventID_Logout           = 3002,
    BlcDmxFilter_EventID_TSData         = 3003,
    BlcKey_EventID_KeyValue             = 3004,
    BlcPlayCtl_EventID_MwReturn         = 3005,

    BlcRes_EventID_ResoureRequest       = 3006,
    BlcRes_EventID_ServiceNotice        = 3007,

    BlcPlayCtl_EventID_ConnectServer    = 3008,

    BlcKey_EventID_KeyDevPlug           = 3101,
} Blc_EventID;


typedef enum {
    BlcKeyDevPlugType_KeyboardPlugin        = 1,
    BlcKeyDevPlugType_KeyboardPlugout       = 2,
    BlcKeyDevPlugType_MousePlugin           = 3,
    BlcKeyDevPlugType_MousePlugout          = 4,
    BlcKeyDevPlugType_ConsolePlugin         = 5,
    BlcKeyDevPlugType_ConsolePlugout        = 6,
} BlcKeyDevPlugType;


typedef enum {
    BlcTermKeyDevType_Irr               = 1,
    BlcTermKeyDevType_Keyboard      = 2,
    BlcTermKeyDevType_Mouse         = 3,
    BlcTermKeyDevType_Console       = 4,
} BlcTermKeyDevType;


typedef enum {
    BlcMousePropertyValue_DEFAULT        = 0,
    BlcMousePropertyValue_BUTTONLEFT     = 1,
    BlcMousePropertyValue_BUTTONMIDDLE   = 2,
    BlcMousePropertyValue_BUTTONRIGHT    = 3,
} BlcMouseKeyValue;

typedef struct {
    int    keydev;     //键值设备类型
    int    keystate;   // 键值状态;
    int    keyvalue;   // 键值
    short   x;          //鼠标的x坐标
    short   y;          //鼠标的y坐标
} BlcKeyValueData;
struct input_event ev_temp;
int func(int fd)
{

    BlcKeyValueData key_info;
    int count;
    int plug_flag = BlcKeyDevPlugType_MousePlugout;

    //  struct input_event ev_temp;  

    if(fd != -1) {  
        plug_flag = BlcKeyDevPlugType_MousePlugin;  
    }  

    char up[] = "抬起";
    char down[] = "按下";

    //while(1) 

    count = read(fd, &ev_temp, sizeof(struct input_event));
    if(count > 0)
    {
        if(ev_temp.type == EV_SYN)
            return 1;

        printf("$$$$$$$$$$$$$$$:  %d, %d, %d\n", ev_temp.type, ev_temp.code, ev_temp.value);    
        printf("key:%d ", ev_temp.code);
        printf("%s\n", ev_temp.value?down:up);

        memset(&key_info, 0 , sizeof(BlcKeyValueData));
        if (ev_temp.type == EV_KEY)
        {
            if (ev_temp.code >= 0  && ev_temp.code <= 127)
            {
                key_info.keydev = BlcTermKeyDevType_Keyboard;
                key_info.keyvalue = ev_temp.value; 
            }
            else if (ev_temp.code >= 0x110  && ev_temp.code <= 0x116)
            {
                key_info.keydev = BlcTermKeyDevType_Mouse;

                if (ev_temp.code == 0x110)
                    key_info.keyvalue = BlcMousePropertyValue_BUTTONLEFT; 
                else if (ev_temp.code == 0x111)
                    key_info.keyvalue = BlcMousePropertyValue_BUTTONRIGHT; 
                else if (ev_temp.code == 0x112)
                    key_info.keyvalue = BlcMousePropertyValue_BUTTONMIDDLE; 
            }   

            if (ev_temp.value == 1)
                key_info.keystate = BlcTermKeyDevStat_Down;
            else if (ev_temp.value == 0)
                key_info.keystate = BlcTermKeyDevStat_Up;

            key_info.x = -1;
            key_info.y = -1;
        }   
        else if (ev_temp.type == EV_REL)
        {
            key_info.keydev = BlcTermKeyDevType_Mouse;
            key_info.keystate = BlcTermKeyDevStat_Default;
            key_info.keyvalue = 0;
            if (ev_temp.code == REL_X)
                b_cur_x += ev_temp.value;
            else if (ev_temp.code == REL_Y)
                b_cur_y += ev_temp.value;
            else if (ev_temp.code == REL_WHEEL)
                ;//???//key_info.keyvalue = ev_temp.code;
            if (b_cur_x < 0) b_cur_x = 0;
            if (b_cur_x > 1280) b_cur_x = 1280;
            if (b_cur_y < 0) b_cur_y = 0;
            if (b_cur_y > 720) b_cur_y = 720;

            key_info.x = b_cur_x;
            key_info.y = 0 - b_cur_y;
        }

        printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:  %d, %d, %d\n", key_info.keydev, key_info.keyvalue, key_info.keyvalue);              


    }
    else if (count == -1)
    {   
        if (plug_flag == BlcKeyDevPlugType_MousePlugin)
        {
            close(fd);
            plug_flag = BlcKeyDevPlugType_MousePlugout;

            printf("plug out !\n");
        }


        if (fd != -1)
        {
            plug_flag = BlcKeyDevPlugType_MousePlugin;
            printf("plug int ok !\n");
        }
        else
        {
            printf("plug int fail !\n");
            usleep(500);
        }
    }
    //}  



}





int main(void)   

{

    int fd_key,fd_ts, fd_led, fd_max, fd_0, fd_2, fd_3;

    struct input_event event_key,event_ts;

    int dac_value;

    struct timeval select_timeout;   

    fd_set readfds;    
    //cat /proc/bus/devices
    select_timeout.tv_sec  = 20;

    select_timeout.tv_usec = 0;     
    fd_0  = open("/dev/input/event0", O_RDWR);

    fd_key = open("/dev/input/event1", O_RDWR);

    fd_2 =   open("/dev/input/event2", O_RDWR);
    fd_3 =   open("/dev/input/event3", O_RDWR);
    fd_ts =  open("/dev/input/event4", O_RDWR);    


    if (fd_key>fd_ts)
        fd_max = fd_key;
    else 
        fd_max = fd_ts; 
    while(1)   
    {      FD_ZERO(&readfds);
        FD_SET(fd_key, &readfds);
        FD_SET(fd_ts, &readfds);   
        FD_SET(fd_0,  &readfds); 
        FD_SET(fd_2,  &readfds);
        FD_SET(fd_3,  &readfds);
        select_timeout.tv_sec= 2;    
        select_timeout.tv_usec = 0;    
        select(fd_max + 1, &readfds, NULL, NULL, &select_timeout);
        if(FD_ISSET(fd_0, &readfds))
        {
            printf("come from fd_0\n");
            func(fd_0);


        }
        if(FD_ISSET(fd_2, &readfds))
        {
            printf("come from fd_2\n");
            func(fd_2);


        }
        if(FD_ISSET(fd_3, & readfds))
        {
            printf("come from fd_3\n");
            func(fd_3);


        }
        if ( FD_ISSET(fd_key, &readfds))    
        {
            printf("come from keyborad\n");    
            func(fd_key);

        }      
        else if(FD_ISSET(fd_ts, &readfds))
        {    
            printf("come from mouse\n");
            func(fd_ts);  

        }       
        printf("|\n|\n");    
    }
}

