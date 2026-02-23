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
    "--kwd <command name>","","Specify the name you want to search for. Searches for partial matches."
    "--match_mode <mode condition>","","Specify the mode condition of the command you want to search in. Searches for partial matches."
    "--match_cmd <cmd condition>","","Specify the cmd condition of the command you want to search in. Searches for partial matches."
    "--match_opt <opt condition>","","Specify the opt name of the command you want to search in."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."
    "--groups <group name>","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

cmd ( load ) : `cmdbox -m cmd -c load <Option>`
========================================================================================

- Obtains the contents of commands under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data folder>","","When omitted, `$HONE/.{self.ver.__appid__}` is used."
    "--title <title>","","Specify the name of the command to be read."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."
    "--groups <group name>","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

