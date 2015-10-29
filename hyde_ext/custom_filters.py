# Source: https://groups.google.com/forum/#!topic/hyde-dev/0vdPY_xhgXc

from hyde.plugin import Plugin
from jinja2 import environmentfilter, Environment


debug_attr_fmt = '''name:  %s
type:  %r
value: %r'''

@environmentfilter
def debug_attr(env, value, verbose=False):
    '''
    A jinja2 filter that creates a <pre> block
    that lists all the attributes of a given object
    inlcuding the value of those attributes and type.

    This filter takes an optional variable "verbose",
    which prints underscore attributes if set to True.
    Verbose printing is off by default.
    '''

    begin = "<pre class='debug'>\n"
    end = "\n</pre>"

    result = ["{% filter escape %}"]
    for attr_name in dir(value):
        if not verbose and attr_name[0] == "_":
            continue
        a = getattr(value, attr_name)
        result.append(debug_attr_fmt % (attr_name, type(a), a))
    result.append("{% endfilter %} ")
    tmpl = Environment().from_string("\n\n".join(result))

    return begin + tmpl.render() + end

    #return "\n\n".join(result)

# list of custom-filters for jinja2
filters = {
        'debug_attr' : debug_attr
        }

class CustomFilterPlugin(Plugin):
    '''
    The curstom-filter plugin allows any
    filters added to the "filters" dictionary
    to be added to hyde
    '''
    def __init__(self, site):
        super(CustomFilterPlugin, self).__init__(site)

    def template_loaded(self,template):
        super(CustomFilterPlugin, self).template_loaded(template)
        self.template.env.filters.update(filters)
