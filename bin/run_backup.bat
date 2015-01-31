@ECHO OFF

REM DEFAULT PROGRAM AND VARIABLE LOCATIONS (NO CHANGE NECESSARY)
REM ------------------------------------------------------------

REM Location of rsync Program
SET RSYNCHOME=C:\cygwin\bin

REM Set CYGWIN variable to 'nontsec'. That makes sure that permissions
REM on your windows machine are not updated as a side effect of cygwin
REM operations.
SET CYGWIN=nontsec

REM Set HOME variable to your windows home directory. That makes sure 
REM that ssh command creates known_hosts in a directory you have access.
REM      SET HOME=%HOMEDRIVE%%HOMEPATH%

REM Make rsync home as a part of system PATH to find required DLLs
SET PATH=%RSYNCHOME%;%PATH%

REM | RSYNC COMMAND SAMPLES
REM | ---------------------
REM | 
REM | Several sample rsync configurations are listed below, along with notes on 
REM | each one. You should use these to guide your setup of your own rsync commands.
REM |
REM | If you have multiple servers, be sure to specify which backup directory you
REM | want your files backed up into. Your ExaVault account comes with nine by default:
REM | backup-1, backup-2, ... , backup-9. We recommend using backup-1 for all data from the
REM | first server, backup-2 for all data from the second server, and so on.
REM |
REM | We recommend you consider using the --delete option when running rsync, which makes
REM | sure that your backup files stay in sync with your production files by deleting any
REM | files in the backup that you've deleted on your main server.
REM |
REM | Windows paths may contain a colon (:) as a part of drive designation and 
REM | backslashes (example c:\, g:\). However, in rsync syntax, a colon in a 
REM | path means searching for a remote host. Solution: use absolute path 'a la unix', 
REM | replace backslashes (\) with slashes (/) and put -/cygdrive/- in front of the 
REM | drive letter:
REM | 
REM | Example : C:\WORK\* --> /cygdrive/c/work/*
REM |
REM | IMPORTANT: BE SURE TO REPLACE 'USERNAME' WITH YOUR ACTUAL EXAVAULT USERNAME
REM |            BEFORE USING THE SAMPLES BELOW. 
REM |
REM |
REM | Example 1 - Backup C:/Inetpub to the 'backup-1' folder on ExaVault
REM |     rsync -avz --delete -e "ssh -i /cygdrive/c/backup/ssh_key" "/cygdrive/c/Inetpub" USERNAME@USERNAME.exavault.com:backup-1
REM |
REM |
REM | Example 2 - Backup your Documents and Settings folder to the 'backup1' folder on ExaVault
REM |     rsync -avz --delete -e "ssh -i /cygdrive/c/backup/ssh_key" "/cygdrive/c/Documents and Settings/" USERNAME@USERNAME.exavault.com:backup-1
REM |
REM | 
REM | Example 3 - Backup the entire C: drive to 'backup5' folder on ExaVault
REM |             Note: When backing up the entire drive, we have to use the '--exclude from' 
REM |             rsync option to exclude files that are in use, such as the Windows Swap file
REM |             and temp files. A sample exclude-from list is included with this script,
REM | 		      and should be stored in C:/backup/
REM | 	  rsync -avz --delete --exclude-from "/cygdrive/c/backup/backup-exclude.txt" -e "ssh -i /cygdrive/c/backup/ssh_key" "/cygdrive/c/" USERNAME@USERNAME.exavault.com:backup-5
REM |

REM RSYNC COMMANDS (CHANGE!!!)
REM --------------------------

REM Here is where you put the actual commands that run. Copy and paste the 
REM examples above down here, and then run the script from the command line to make sure
REM everything worked. Once it does, you can set it up to run from Windows Task Manager

REM Palm info.
rsync -av --delete "/cygdrive/c/progs/palm/BradyM" /cygdrive/f/backups/red_palm

REM Firefox bookmarks.
rsync -av --delete "/cygdrive/c/Users/mbrady/AppData/Roaming/Mozilla/Firefox/Profiles/3b1enpoo.default/bookmarks.html" /cygdrive/f/backups/red_bookmarks

REM The Desktop folder.
rsync -av --delete "/cygdrive/c/Users/mbrady/Desktop" /cygdrive/f/backups/red_desktop

REM The 'mbrady' folder.
rsync -av --delete "/cygdrive/c/Users/mbrady/Documents/mbrady" /cygdrive/f/backups/red_mbrady
