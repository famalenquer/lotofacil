@echo off
color 0A
title Lotofacil Pro Analytics - Backup na Nuvem (GitHub)

echo =======================================================
echo     Sincronizando Lotofacil Pro Analytics com o GitHub
echo =======================================================
echo.

cd /d C:\wamp64\www\lotofacil

echo [1/3] Identificando arquivos novos ou modificados...
"C:\Program Files\Git\cmd\git.exe" add .

echo [2/3] Empacotando atualizacoes (Commit)...
"C:\Program Files\Git\cmd\git.exe" commit -m "Atualizacao automatica via Script Batch"

echo [3/3] Enviando para a nuvem de forma segura (Push)...
"C:\Program Files\Git\cmd\git.exe" push origin main

echo.
echo =======================================================
echo     Sincronizacao Concluida! Tudo salvo no GitHub.
echo =======================================================
echo.
pause
