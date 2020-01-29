import jinja2

def render_template(template, context):
    env = jinja2.Environment(autoescape=True)
    t = env.from_string(template)
    return t.render(**context)
