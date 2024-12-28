import datetime

dt_now = datetime.datetime(2024, 12, 28)
__appid__ = 'cmdbox'
__title__ = 'cmdbox'
__version__ = '0.2.3.2'
__copyright__ = f'Copyright © 2023-{dt_now.strftime("%Y")} hamacom2004jp'
__pypiurl__ = 'https://pypi.org/project/cmdbox/'
__srcurl__ = 'https://github.com/hamacom2004jp/cmdbox'
__docurl__ = 'https://hamacom2004jp.github.io/cmdbox/index.html'
# https://patorjk.com/software/taag/#p=display&f=ANSI%20Shadow&t=cmdbox
__logo__ = '''
 ██████╗███╗   ███╗██████╗ ██████╗  ██████╗ ██╗  ██╗
██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝
██║     ██╔████╔██║██║  ██║██████╔╝██║   ██║ ╚███╔╝ 
██║     ██║╚██╔╝██║██║  ██║██╔══██╗██║   ██║ ██╔██╗ 
╚██████╗██║ ╚═╝ ██║██████╔╝██████╔╝╚██████╔╝██╔╝ ██╗
 ╚═════╝╚═╝     ╚═╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝'''
__description__ = f'{__title__} {__version__}\n\n' + \
                  f'{__copyright__}\n' + \
                  f'Web Site: PyPi <{__pypiurl__}>\n' + \
                  f'Web Site: SorceCode <{__srcurl__}>\n' + \
                  f'Web Site: Document <{__docurl__}>\n' + \
                  f'License: MIT License <https://opensource.org/license/mit/>\n' + \
                  f'This is free software: you are free to change and redistribute it.\n' + \
                  f'There is NO WARRANTY, to the extent permitted by law.'
__all__ = ['__logo__', '__title__', '__version__', '__copyright__', '__srcurl__', '__docurl__']