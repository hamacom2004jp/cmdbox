from rich.console import Console
from rich import highlighter
from rich.theme import Theme
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

    product_word = re.compile(r"CMDBOX|IINFER|USOUND|GAIAN|GAIC|WITSHAPE", re.IGNORECASE)
    success_word = re.compile(r"SUCCESS|OK|PASSED|DONE|COMPLETE|START|FINISH|OPEN|CONNECTED|ALLOW|EXEC", re.IGNORECASE)
    warning_word = re.compile(r"WARNING|WARN|CAUTION|NOTICE|STOP|DISCONNECTED|DENY", re.IGNORECASE)
    error_word = re.compile(r"ERROR|ALERT|CRITICAL|FATAL|ABORT|FAILED", re.IGNORECASE)

def colorize(s:str, *colors:int) -> str:
    return Colors.S + Colors.D.join(map(str, [Colors.ResetAll]+list(colors))) + Colors.E + s + Colors._colorize_suffix

def colorize_msg(msg) -> str:
    msg = Colors.success_word.sub(colorize(r"\g<0>", Colors.Green), msg)
    msg = Colors.warning_word.sub(colorize(r"\g<0>", Colors.Yellow), msg)
    msg = Colors.error_word.sub(colorize(r"\g<0>", Colors.Red), msg)
    msg = Colors.product_word.sub(colorize(r"\g<0>", Colors.LightBlue), msg)
    return msg

level_mapping = {
    logging.DEBUG:   f"{colorize('DEBUG', Colors.Bold, Colors.Cyan)}",
    logging.INFO:    f"{colorize('INFO', Colors.Bold, Colors.Green)} ",
    logging.WARNING: f"{colorize('WARN', Colors.Bold, Colors.Yellow)} ",
    logging.ERROR:   f"{colorize('ERROR', Colors.Bold, Colors.Red)}",
    logging.CRITICAL:f"{colorize('FATAL', Colors.Bold, Colors.LightGray, Colors.BackgroundRed)}"}

level_mapping_nc = {
    logging.DEBUG:   f"DEBUG",
    logging.INFO:    f"INFO ",
    logging.WARNING: f"WARN ",
    logging.ERROR:   f"ERROR",
    logging.CRITICAL:f"FATAL"}

theme=Theme({
    "repr.log_debug": "bold cyan",
    "repr.log_info": "bold green",
    "repr.log_warn": "bold Yellow",
    "repr.log_error": "bold red",
    "repr.log_fatal": "bold red reverse",
    "repr.log_product": "dodger_blue2 reverse",
    "repr.log_success": "green",})

class LogLevelHighlighter(highlighter.ReprHighlighter):
    def __init__(self):
        #self.highlights = []
        self.highlights.append(r"(?P<log_debug>DEBUG)")
        self.highlights.append(r"(?P<log_info>INFO)")
        self.highlights.append(r"(?P<log_warn>WARN|WARNING|WARN|CAUTION|NOTICE|STOP|DISCONNECTED|DENY)")
        self.highlights.append(r"(?P<log_error>ERROR|ALERT|ABORT|FAILED)")
        self.highlights.append(r"(?P<log_fatal>FATAL|CRITICAL)")
        self.highlights.append(r"(?P<log_product>CMDBOX|IINFER|USOUND|GAIAN|GAIC|WITSHAPE)")
        self.highlights.append(r"(?P<log_success>SUCCESS|OK|PASSED|DONE|COMPLETE|START|FINISH|OPEN|CONNECTED|ALLOW|EXEC)")
        """
        self.highlights.append(r"(?P<tag_start><)(?P<tag_name>[-\w.:|]*)(?P<tag_contents>[\w\W]*)(?P<tag_end>>)")
        self.highlights.append(r'(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?')
        self.highlights.append(r"(?P<brace>[][{}()])")
        self.highlights.append(highlighter._combine_regex(
            r"(?P<ipv4>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
            r"(?P<ipv6>([A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4})",
            r"(?P<eui64>(?:[0-9A-Fa-f]{1,2}-){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\.){3}[0-9A-Fa-f]{4})",
            r"(?P<eui48>(?:[0-9A-Fa-f]{1,2}-){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})",
            r"(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})",
            r"(?P<call>[\w.]*?)\(",
            r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
            r"(?P<ellipsis>\.\.\.)",
            r"(?P<number_complex>(?<!\w)(?:\-?[0-9]+\.?[0-9]*(?:e[-+]?\d+?)?)(?:[-+](?:[0-9]+\.?[0-9]*(?:e[-+]?\d+)?))?j)",
            r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[-+]?\d+?)?\b|0x[0-9a-fA-F]*)",
            r"(?P<path>\B(/[-\w._+]+)*\/)(?P<filename>[-\w._+]*)?",
            r"(?<![\\\w])(?P<str>b?'''.*?(?<!\\)'''|b?'.*?(?<!\\)'|b?\"\"\".*?(?<!\\)\"\"\"|b?\".*?(?<!\\)\")",
            r"(?P<url>(file|https|http|ws|wss)://[-0-9a-zA-Z$_+!`(),.?/;:&=%#~@]*)",
        ))
        """
        self.highlights = [re.compile(h, re.IGNORECASE) for h in self.highlights]

class ColorfulStreamHandler(logging.StreamHandler):
    console = Console(soft_wrap=True, height=True, highlighter=LogLevelHighlighter(), theme=theme)

    def emit(self, record: logging.LogRecord) -> None:
        #record.levelname = level_mapping[record.levelno]
        #record.asctime = colorize(record.asctime, Colors.Bold)
        #record.msg = colorize_msg(record.msg)
        #super().emit(record)
        record.levelname = level_mapping_nc[record.levelno]
        record.msg = self.format(record)
        self.console.print(record.msg)

class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = level_mapping_nc[record.levelno]
        super().emit(record)

