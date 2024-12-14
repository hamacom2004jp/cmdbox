import datetime

dt_now = datetime.datetime(2024, 12, 14)
__appid__ = 'sample'
__title__ = 'sample'
__version__ = '0.1.0'
__copyright__ = f'Copyright © 2023-{dt_now.strftime("%Y")} XXXXXXXX'
__logo__ = '''
███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗
██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝
███████╗███████║██╔████╔██║██████╔╝██║     █████╗  
╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  
███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝'''
__description__ = f'{__title__} {__version__}\n\n' + \
                  f'{__copyright__}\n' + \
                  f'License: MIT License <https://opensource.org/license/mit/>\n' + \
                  f'This is free software: you are free to change and redistribute it.\n' + \
                  f'There is NO WARRANTY, to the extent permitted by law.'
__all__ = ['__logo__', '__title__', '__version__', '__copyright__']