from ..template import get_env

__all__ = ["render_template"]

env = get_env(__file__)


def render_template(template_name, *args, **kwargs):
    info = {}
    for current_info in args:
        info.update(current_info)
    info.update(kwargs)
    template = env.get_template(template_name)
    return template.render(info)
