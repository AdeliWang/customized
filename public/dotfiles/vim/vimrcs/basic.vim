" write by orjan
"
" =====================================================================
" Newish {
    set encoding=utf-8
    set fileencoding=UTF-8
    set fileencodings=ucs-bom,utf-8,default,gb2312
    set termencoding=utf-8    

    set fencs=utf-8,gbk
    set formatlistpat=^\\s*\\(\\d\\\|[-*]\\)\\+[\\]:.)}\\t\ ]\\s* "and bullets, too
    set viminfo+=! " Store upper-case registers in viminfo
    "set nomore " Short nomore
   
    set ffs=unix,dos,mac " Use Unix as the standard file type
" }

" Basics {
    set undodir=~/.vimundo/
    set undofile
    set history=50
    set nowritebackup
    set nobackup
    set incsearch
    set hlsearch
    :hi Search ctermbg=7

    "set noexrc           "  don't use local version of .(g)vimrc, .exrc
    set cpoptions=aABceFsmq
    "             |||||||||
    "             ||||||||+-- When joining lines, leave the cursor
    "             |||||||      between joined lines
    "             |||||||+-- When a new match is created (showmatch)
    "             ||||||      pause for .5
    "             ||||||+-- Set buffer options when entering the
    "             |||||      buffer
    "             |||||+-- :write command updates current file name
    "             ||||+-- Automatically add <CR> to the last line
    "             |||      when using :@r
    "             |||+-- Searching continues at the end of the match
    "             ||      at the cursor position
    "             ||+-- A backslash has no special meaning in mappings
    "             |+-- :write updates alternative file name
    "             +-- :read updates alternative file name
" } 

" General {
    "set autochdir              " always switch to the current file directory
    set magic                   " For regular expressions turn magic on
    set autowrite
    set autoread
    filetype plugin on
    filetype indent on

    "set hidden
    set bufhidden=hide
    " set clipboard=unnamed
    set clipboard+=unnamed          " share windows clipboard ??
    set mouse=a                     " use mouse everywhere
    set selection=exclusive
    set selectmode=mouse,key    

    let mapleader = ","
    let g:mapleader = ","
" }

" Vim UI {
    set ruler                    "Always show current position
    set colorcolumn=120          " highligth column 120
    "set cursorcolumn            " highlight the current column
    "set cursorline              " highlight current line
    set linespace=0              " don't insert any extra pixel lines betweens rows
    "set list                     " we do what to show tabs, to ensure we get them out of my files
    "set listchars=tab:>-,trail:- " show tabs and trailing
    set nostartofline            " leave my cursor where it was
    set number                   " turn on line numbers
    "set relativenumber          " turn on relative line numbers
    set numberwidth=4            " We are good up to 9999 lines
    "set report=0                 " tell us when anything is changed via :...
    set scrolloff=3              " Keep 3 lines (top/bottom) for scope
    set shortmess=aOstT          " shortens messages to avoid 'press a key' prompt
    set showcmd                  " show the command being typed
    set cmdheight=1
    set sidescrolloff=3          " Keep 3 lines at the size

    "colorscheme peaksea "solarized
    set background=dark
    let g:solarized_termcolors=256
    " Don't redraw while executing macros (good performance config)
    set lazyredraw 
" }

" status line {
    set laststatus=2
    set statusline=\ %{HasPaste()}%<%-15.25(%f%)%m%r%h\ %w\ \
    set statusline+=\ \ \ [%{&ff}/%Y]
    set statusline+=\ \ \ %<%20.30(%{hostname()}:%{CurDir()}%)\
    set statusline+=%=%-10.(%l,%c%V%)\ %p%%/%L
    function! CurDir()
        let curdir = substitute(getcwd(), $HOME, "~", "")
        return curdir
    endfunction
   " function! HasPaste()
   "     if &paste
   "         return '[PASTE]'
   "     else
   "         return ''
   "     endif
   " endfunction
"}

" Text Formatting/Layout {
    syntax enable
    "set wildmenu
    set wildmode=list:longest:full   " turn on wild mode huge list
    " ignore these list file extensions
    set wildignore=*.dll,*.o,*.obj,*.bak,*.exe,*.pyc,*.jpg,*.gif,*.png,*.so,*.a
    if has("win16") || has("win32")
        set wildignore+=*/.git/*,*/.hg/*,*/.svn/*,*/.DS_Store
    else
        set wildignore+=.git\*,.hg\*,.svn\*
    endif
    
    " Configure backspace so it acts as it should act
    set backspace=eol,start,indent
    set whichwrap+=<,>,h,l
    "(XXX: #VIM/tpope warns the line below could break things)
    set iskeyword+=_,$,@,%,#         " none of these are word dividers

    set completeopt=menu,menuone,longest " show pop up menu for completions
    "set formatoptions=rq   " Automatically insert comment leader on return,and let gq format comments 
    set formatoptions=tcrqn
    set ignorecase         " case insensitive by default
    set infercase          " case inferred by default
    set nowrap             " do not wrap line
    set shiftround         " when at 3 spaces, and I hit > ... go to 4, not 5
    set smartcase          " if there are caps, go case-sensitive
    set shiftwidth=4       " auto-indent amount when using cindent, >>, << and stuff like that
    set softtabstop=4      " when hitting tab or backspace, how many spaces should a tab be
    set tabstop=4          
    "set smarttab          " ????
    set expandtab          " no real tabs please!
    autocmd filetype css,html,Makefile set noexpandtab
    autocmd filetype python retab

    "set cindent
    "set foldmethod=syntax
    set foldcolumn=0        " columns for folding
    set foldmethod=indent
    set foldlevel=9
    set nofoldenable        "dont fold by default "

    set ai "Auto indent
    set si "Smart indent
    set wrap "Wrap lines
" }

" source $VIMRUNTIME/vimrc_example.vim    " unusable 

"" let g:pydiction_location = '~/.vim/bundle/pydiction/complete-dict'

"" EOF
