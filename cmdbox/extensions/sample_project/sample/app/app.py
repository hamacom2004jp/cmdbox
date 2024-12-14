from cmdbox.app import app
from sample import version


def main(args_list:list=None):
    _app = app.CmdBoxApp.getInstance(appcls=SampleApp, ver=version)
    return _app.main(args_list)[0]

class SampleApp(app.CmdBoxApp):
    pass