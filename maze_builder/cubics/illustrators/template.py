import pkgutil
import jinja2
import random


RESOURCE_PACKAGE = 'maze_builder.cubics.resources'


def resource(resource_name):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode('utf-8')


def template(template_name, **kwargs):
    return jinja2.Template(resource(template_name)).render(**kwargs)


class CubicTemplateIllustrator(object):
    def __init__(self, template='satellite.pov.jinja2'):
        self.template = template

    def draw(self, cubic):
        return template(
            self.template,
            connections=cubic.topology.active_routes,
            walls=cubic.topology.inactive_routes(),
            center=cubic.center(),
            seed=random.randint(1, 30000),
        )
