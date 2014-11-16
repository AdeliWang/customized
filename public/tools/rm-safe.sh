rm_interactive()
{
    if [ -n "$PS1" ] ; then
        rm () 
        { 
            ls -FCsd "$@"
            echo 'remove[ny]? ' | tr -d '\012' ; read
            if [ "_$REPLY" = "_y" ]; then
                /bin/rm -rf "$@"
            else
                echo '(cancelled)'
            fi
        }
    fi
}
