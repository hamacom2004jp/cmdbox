.. -*- coding: utf-8 -*-

******************************
Command Reference ( cmd mode )
******************************

List of cmd mode commands.

cmd ( list ) : ``cmdbox -m cmd -c list <Option>``
=================================================

- Obtains a list of commands under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","required","When omitted, `$HONE/.cmdbox` is used."
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "--match_mode <match_mode>","","Specify the mode condition of the command you want to search in. Searches for partial matches."
    "--match_cmd <match_cmd>","","Specify the cmd condition of the command you want to search in. Searches for partial matches."
    "--match_opt <match_opt>","","Specify the opt name of the command you want to search in."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

cmd ( load ) : ``cmdbox -m cmd -c load <Option>``
=================================================

- Obtains the contents of commands under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","required","When omitted, `$HONE/.cmdbox` is used."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."
    "--cmd_title <cmd_title>","required","Specify the name of the command to be read."
