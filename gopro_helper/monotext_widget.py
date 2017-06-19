
import ipywidgets


# <pre style="font-family:  DejaVu Sans Mono, Consolas, Lucida Console, Monospace;'


_html_template = """
<pre style="font-family:  Monospace;'
            display:      block;
            margin:       0em 0;
            white-space:  pre;
            font-variant: normal;
            font-weight:  normal;
            font-style:   normal;
            font-size:    14px;">
{content:}
</pre>
"""


class MonoText(ipywidgets.HTML):
    """Monospace text version of ipywidget.Text widget
    """
    _text = ''
    def __init__(self, text=None):
        super().__init__()
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, list_or_string):
        if not list_or_string:
            return

        if isinstance(list_or_string, str):
            list_or_string = [list_or_string]

        if not isinstance(list_or_string, list):
            msg = 'Input item must be a string or list of strings: {}'.format(type(list_or_string))
            raise ValueError(msg)

        if not isinstance(list_or_string[0], str):
            msg = 'Input item(s) must be a string or list of strings: {}'.format(type(list_or_string[0]))
            raise ValueError(msg)

        self._text = '\n'.join(list_or_string)
        self.value = _html_template.format(content=self._text)

#------------------------------------------------

if __name__ == '__main__':
    pass

