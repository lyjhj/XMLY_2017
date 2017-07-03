# coding=utf-8
import textract
from haystack.utils import Highlighter
from django.utils.html import strip_tags


# 继承重写高亮标签
class MyHighlighter(Highlighter):
    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        start_offset, end_offset = self.find_window(highlight_locations)

        # this is my only edit here, but you'll have to experiment
        start_offset = 0
        return self.render_html(highlight_locations, start_offset, end_offset)

# 读取pdf到string
def parse_to_string(filename):
	return textract.process(filename)