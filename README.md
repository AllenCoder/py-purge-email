# py-purge-email
Deletes all messages of a certain age, using IMAP, from an email account.

Use at your own risk!

PyPurge Email V1.0
==================
Andrew Johnson
ad.johnson@ntlworld.com
06 Nov 2019


This Python 3 program will scan an email account using IMAP for messages older than
a certain age and delete them.

Old email can be deleted from all folders or each folder.

Because of the length of time bulikng deleting takes, folders can be scanned first
then the deletions can be left running (which might take several hours for many
thousands of messages.)

After running this, you may need to "empty" your deleted items/Trash folder to recover the space.
With hotmail/live/outlook accounts (i.e. online Microsoft ones) you will need to manually empty "recoverable items" too.
This is done within the "deleted items" folder when viewing your webmail.
