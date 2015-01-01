#include <termios.h>
#include <string.h>

int set_newinput_mode( struct termios *org_opts )
{
    int ret;
    struct termios new_opts;

    /* store old settings */
    ret = tcgetattr( STDIN_FILENO, org_opts );
    if ( ret < 0 )
    {
        printf( "error: tcgetattr()" );
        return 1;
    }

    /* set new terminal parms */
    memcpy( &new_opts, org_opts, sizeof(new_opts) );
    new_opts.c_lflag &= ~(ICANON | ECHO | ECHOE | ECHOK | ECHONL | ECHOPRT | ECHOKE | ICRNL);
    ret = tcsetattr( STDIN_FILENO, TCSANOW, &new_opts );
    if ( ret < 0 )
    {
        printf( "error: tcsetattr()" );
        return 1;
    }

    return 0;
}

int restore_input_mode( struct termios *org_opts )
{
    int ret;
    ret = tcsetattr( STDIN_FILENO, TCSANOW, org_opts );
    if ( ret < 0 )
    {
        printf( "error: tcsetattr()" );
        return 1;
    }

    return 0;
}

int main( void )
{
    int ret,i;
    char c;

    fd_set read_fd_set;
    struct timeval timeout;
    int keyboard = 0;
    struct termios org_opts;
#if 1
    keyboard = open( "/dev/tty", O_RDONLY | O_NONBLOCK );
    if ( keyboard < 0 )
    {
        printf( "error: open /dev/tty\n" );
    }
#endif

    set_newinput_mode( &org_opts );

    while (1)
    {
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        FD_ZERO( &read_fd_set );
        FD_SET( keyboard, &read_fd_set );

        ret = select( keyboard+1, &read_fd_set, NULL, NULL, &timeout );
        if ( ret < 0 )
        {
            perror( "select()" );
        }
        else if ( ret == 0 )
        {
            printf( "timeout\n" );
        }
        else
        {
            printf( "ret = %d: the status of keyboard is changed\n.", ret );
        }

        if ( FD_ISSET( keyboard, &read_fd_set ) )
        {
            i = read( keyboard, &c, 1 );

            printf("you press: %c\n",c);

            if ( 'q' == c || 'Q' == c )
                break;
        }
    }

    restore_input_mode( &org_opts );

    return 0;
}
