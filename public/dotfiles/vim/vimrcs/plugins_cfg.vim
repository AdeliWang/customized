" // 
let g:pydiction_location = '~/.vim/bundle/pydiction/complete-dict'

" Taglist {
    let Tlist_Ctags_Cmd ='/usr/local/bin/ctags'
    " Taglist plugin mapping
    " Taglist plugin config
    let Tlist_Use_Right_Window = 1
    let Tlist_Inc_Winwidth = 0
    let Tlist_WinWidth = 30
    let Tlist_GainFocus_On_ToggleOpen = 0
    let Tlist_Show_One_File = 1
    let Tlist_Exit_OnlyWindow = 1
    let Tlist_Use_SingleClick = 1
    " let Tlist_Auto_Open = 1
    " let Tlist_File_Fold_Auto_Close = 1
    autocmd BufWritePost *.cpp :TlistUpdate
    autocmd BufWritePost *.h :TlistUpdate
    autocmd BufWritePost *.jce :TlistUpdate
" }


"""""""""" NerdTree (and vimenter events)
" nnoremap <C-n> :NERDTreeToggle<CR>
autocmd vimenter *.cpp NERDTree
autocmd vimenter *.cpp Tlist
autocmd vimenter *.cpp SrcExpl
autocmd VimEnter *.cpp wincmd w

"autocmd BufNew   * wincmd p
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTreeType") && b:NERDTreeType == "primary") | q | endif

"""""""""" Function for NerdTree + Taglist (auto close when 2 windows)

function! CheckLeftBuffers()
  if tabpagenr('$') == 1
    let i = 1
    while i <= winnr('$')
      " echom getbufvar(winbufnr(i), '&buftype')
      if getbufvar(winbufnr(i), '&buftype') == 'help' ||
          \ getbufvar(winbufnr(i), '&buftype') == 'quickfix' ||
          \ exists('t:NERDTreeBufName') &&
          \   bufname(winbufnr(i)) == t:NERDTreeBufName ||
          \ bufname(winbufnr(i)) == '__Tag_List__' ||
          \ bufname(winbufnr(i)) == 'Source_Explorer' ||
          \ getwinvar(i, 'SrcExpl') == 1
        let i += 1
      else
        break
      endif
    endwhile
    if i == winnr('$') + 1
      qall
    endif
    unlet i
  endif
endfunction
autocmd BufEnter * call CheckLeftBuffers()

" autocmd vimenter * :SrcExplToggle
" autocmd VimEnter * wincmd p

" nnoremap <CR> <c-w><c-j><CR>
" nnoremap <C-N> :FufTag<CR>
" inoremap <C-N> <esc>:FufTag<CR>

"""""""""" tabline
hi TabLine      ctermfg=Black  ctermbg=Green     cterm=NONE
hi TabLineFill  ctermfg=Black  ctermbg=Green     cterm=NONE
hi TabLineSel   ctermfg=White  ctermbg=DarkBlue  cterm=NONE

"""""""""" airline
let g:airline#extensions#tabline#enabled = 1

"" ========================================================

" // Set the height of Source Explorer window 
let g:SrcExpl_winHeight = 8 

" // Set 100 ms for refreshing the Source Explorer 
let g:SrcExpl_refreshTime = 100 

" // Set "Enter" key to jump into the exact definition context 
let g:SrcExpl_jumpKey = "<ENTER>" 

" // Set "Space" key for back from the definition context 
let g:SrcExpl_gobackKey = "<SPACE>" 

" // In order to avoid conflicts, the Source Explorer should know what plugins
" // except itself are using buffers. And you need add their buffer names into
" // below listaccording to the command ":buffers!"
let g:SrcExpl_pluginList = [ 
        \ "__Tag_List__", 
        \ "_NERD_tree_",
        \ "t:NERDTreeBufName",
        \ "NERD_tree_1"
    \ ] 

" // Enable/Disable the local definition searching, and note that this is not 
" // guaranteed to work, the Source Explorer doesn't check the syntax for now. 
" // It only searches for a match with the keyword according to command 'gd' 
let g:SrcExpl_searchLocalDef = 1 

" // Do not let the Source Explorer update the tags file when opening 
let g:SrcExpl_isUpdateTags = 0 

" // Use 'Exuberant Ctags' with '--sort=foldcase -R .' or '-L cscope.files' to 
" // create/update the tags file 
"let g:SrcExpl_updateTagsCmd = "ctags --sort=foldcase -R ." 
let g:SrcExpl_updateTagsCmd = "tagscope " 

"  update tags {
    function! DelTagOfFile(file)
        let fullpath = a:file
        let cwd = getcwd()
        let tagfilename = cwd . "/tags"
        let f = substitute(fullpath, cwd . "/", "", "")
        let f = escape(f, './')
        let cmd = 'sed -i "/' . f . '/d" "' . tagfilename . '"'
        let resp = system(cmd)
    endfunction
    
    function! UpdateTags()
        let f = expand("%:p")
        let cwd = getcwd()
        let tagfilename = cwd . "/tags"
        "let cmd = 'ctags -a -f ' . tagfilename . ' --c++-kinds=+p --fields=+iaS --extra=+q ' . '"' . f . '"'
        let cmd = 'tagscope '
        call DelTagOfFile(f)
        let resp = system(cmd)
    endfunction
    autocmd BufWritePost *.cpp,*.h,*.c call UpdateTags()
" }


"" easymotion {
    let g:EasyMotion_smartcase = 1 "ignore case
" }
