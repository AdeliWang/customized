:nnoremap <leader><F1> :!less ~/.vimrcs/shutcut.vim<cr>
:nnoremap <leader>sv :source $MYVIMRC<cr>

":noremap <tab> <c-w><c-p>
:noremap <s-tab> <c-w><c-w>

" Disable highlight when <leader><cr> is pressed
map <silent> <leader><cr> :noh<cr>

map f <Plug>(easymotion-prefix)
map ff <Plug>(easymotion-s2)
map fs <Plug>(easymotion-f2)
map fl <Plug>(easymotion-lineforward)
map fj <Plug>(easymotion-j2)
map fk <Plug>(easymotion-k2)
map fh <Plug>(easymotion-linebackward)

set pastetoggle=<F9>
:noremap <leader>m :let &mouse=(&mouse == 'a' ? '' : 'a')<CR>:set paste!<CR>:set nu!<CR>

" Remove the Windows ^M - when the encodings gets messed up
noremap <Leader>M mmHmt:%s/<C-V><cr>//ge<cr>'tzt'm

:noremap <F5> :bp<cr>
:noremap <S-F5> :bn<cr>
nnoremap <leader><F5> :bd#<CR>
" Close the current buffer
map <leader>bd :Bclose<cr>
" Close all the buffers
map <leader>ba :bufdo bd<cr>

:noremap <leader><leader>w :TlistToggle<CR>:NERDTreeToggle<CR>:SrcExplToggle<CR><c-w><c-l>
:noremap <leader><leader>t :TlistToggle<CR><C-W><C-L> 
:noremap <leader><leader>n :NERDTreeToggle<CR><C-W><C-L> 
:noremap <leader><leader>s :SrcExplToggle<CR><C-W><C-L> 

" SrcExplToggle {
    " // Set "<leader>s<leader>" key for updating the tags file artificially 
    let g:SrcExpl_updateTagsKey = "<leader>s<leader>" 
    " // Set "<leader>sp" key for displaying the previous definition in the jump list 
    let g:SrcExpl_prevDefKey = "<leader>sp" 
    " // Set "<leader>sn" key for displaying the next definition in the jump list 
    let g:SrcExpl_nextDefKey = "<leader>sn" 
" }

" Fast saving
nmap <leader>w :w!<cr>

" :W sudo saves the file
" (useful for handling the permission-denied error)
command W w !sudo tee % > /dev/null

"""""""""" ctags
"map <C-F12> :!/usr/local/bin/ctags -R --exclude=.git --exclude=log --exclude=wutils --c++-kinds=+p --fields=+iaS --extra=+q *<CR>
" nnoremap <C-[> <C-T>

map <C-F12> :!tagscope <CR>

nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

nmap wv     <C-w>v
nmap ws     <C-w>s
nmap wc     <C-w>c

" Smart way to move between windows
map <C-j> <C-W>j
map <C-k> <C-W>k
map <C-h> <C-W>h
map <C-l> <C-W>l

" Useful mappings for managing tabs
map <leader>tn :tabnew<cr>
map <leader>to :tabonly<cr>
map <leader>tc :tabclose<cr>
map <leader>tm :tabmove 
map <leader>t<leader> :tabnext 

" Let 'tl' toggle between this and the last accessed tab
let g:lasttab = 1
nmap <Leader>tl :exe "tabn ".g:lasttab<CR>
au TabLeave * let g:lasttab = tabpagenr()

" Opens a new tab with the current buffer's path
" Super useful when editing files in the same directory
map <leader>te :tabedit <c-r>=expand("%:p:h")<cr>/

" Switch CWD to the directory of the open buffer
map <leader>cd :cd %:p:h<cr>:pwd<cr>

" Specify the behavior when switching between buffers 
try
  set switchbuf=useopen,usetab,newtab
  set stal=2
catch
endtry

"  EOF
