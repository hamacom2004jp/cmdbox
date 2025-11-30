.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( cml mode )
****************************************************

List of cmd mode commands.

cmd ( list ) : `cmdbox -m cmd -c list <Option>`
========================================================================================

- Obtains a list of commands under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data folder>","","When omitted, `$HONE/.{self.ver.__appid__}` is used."
    "--kwd <command name>","","Specify the name you want to search for. Searches for partial matches."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."
    "--groups <group name>","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

