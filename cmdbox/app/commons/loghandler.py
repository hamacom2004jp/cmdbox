import re
import logging
import logging.handlers

class Colors:
    S = "\033["
    D = ";"
    E = "m"
    # https://pkg.go.dev/github.com/whitedevops/colors
    ResetAll = 0

    Bold       = 1
    Dim        = 2
    Underlined = 4
    Blink      = 5
    Reverse    = 7
    Hidden     = 8

    ResetBold       = 21
    ResetDim        = 22
    ResetUnderlined = 24
    ResetBlink      = 25
    ResetReverse    = 27
    ResetHidden     = 28

    Default      = 39
    Black        = 30
    Red          = 31
    Green        = 32
    Yellow       = 33
    Blue         = 34
    Magenta      = 35
    Cyan         = 36
    LightGray    = 37
    DarkGray     = 90
    LightRed     = 91
    LightGreen   = 92
    LightYellow  = 93
    LightBlue    = 94
    LightMagenta = 95
    LightCyan    = 96
    White        = 97

    BackgroundDefault      = 49
    BackgroundBlack        = 40
    BackgroundRed          = 41
    BackgroundGreen        = 42
    BackgroundYellow       = 43
    BackgroundBlue         = 44
    BackgroundMagenta      = 45
    BackgroundCyan         = 46
    BackgroundLightGray    = 47
    BackgroundDarkGray     = 100
    BackgroundLightRed     = 101
    BackgroundLightGreen   = 102
    BackgroundLightYellow  = 103
    BackgroundLightBlue    = 104
    BackgroundLightMagenta = 105
    BackgroundLightCyan    = 106
    BackgroundWhite        = 107

    _colorize_suffix = S + str(ResetAll) + E
    
    success_word = re.compile(r"SUCCESS|OK|PASSED|DONE|COMPLETE|START|FINISH|OPEN|CONNECTED|ALLOW", re.IGNORECASE)
    warning_word = re.compile(r"WARNING|WARN|CAUTION|NOTICE|STOP|DISCONNECTED|DENY", re.IGNORECASE)
    error_word = re.compile(r"ERROR|ALERT|CRITICAL|FATAL|ABORT|FAILED", re.IGNORECASE)

def colorize(s:str, *colors:int) -> str:
    return Colors.S + Colors.D.join(map(str, [Colors.ResetAll]+list(colors))) + Colors.E + s + Colors._colorize_suffix

def colorize_msg(msg) -> str:
    msg = Colors.success_word.sub(colorize(r"\g<0>", Colors.Green), msg)
    msg = Colors.warning_word.sub(colorize(r"\g<0>", Colors.Yellow), msg)
    msg = Colors.error_word.sub(colorize(r"\g<0>", Colors.Red), msg)
    return msg

level_mapping = {
    logging.DEBUG:   f"{colorize('DEBUG', Colors.Bold, Colors.Cyan)}:    ",
    logging.INFO:    f"{colorize('INFO', Colors.Bold, Colors.Green)}:     ",
    logging.WARNING: f"{colorize('WARNING', Colors.Bold, Colors.Yellow)}:  ",
    logging.ERROR:   f"{colorize('ERROR', Colors.Bold, Colors.Red)}:    ",
    logging.CRITICAL:f"{colorize('CRITICAL', Colors.Bold, Colors.LightGray, Colors.BackgroundRed)}: "}

level_mapping_nc = {
    logging.DEBUG:   f"DEBUG:    ",
    logging.INFO:    f"INFO:     ",
    logging.WARNING: f"WARNING:  ",
    logging.ERROR:   f"ERROR:    ",
    logging.CRITICAL:f"CRITICAL: "}

class ColorfulStreamHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = level_mapping[record.levelno]
        #record.asctime = colorize(record.asctime, Colors.Bold)
        record.msg = colorize_msg(record.msg)
        super().emit(record)

class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = level_mapping_nc[record.levelno]
        super().emit(record)

