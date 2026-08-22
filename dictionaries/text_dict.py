"""平文テキスト変換用の辞書ファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################

import re

TEXT_EXTENSIONS: set[str] = {".txt"}

TEXT_FORMAT_NAME = "plain_text"

TEXT_PARAGRAPH_SEPARATOR = "\n\n"
TEXT_PARAGRAPH_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(r"\n[ \t]*\n+")
TEXT_LINE_BREAK_HTML = "<br><br>"
TEXT_PARAGRAPH_SPACER_HEIGHT = 24
