from maze_builder.random2 import weighted_choice, Choice


class LineIllustratorBase(object):
    def __init__(self):
        self.image = None

    def __call__(self, cubic):
        return self.draw(cubic)

    def prepare(self, width, height):
        pass

    def draw_wall(self, p0, p1):
        pass

    def draw_feature(self, feature):
        pass

    def draw(self, cubic):
        self.prepare(1+cubic.maxx-cubic.minx, 1+cubic.maxy-cubic.miny)
        z = cubic.minz
        for x in range(cubic.minx, cubic.maxx+2):
            for y in range(cubic.miny, cubic.maxy+2):
                xo = x - cubic.minx
                yo = y - cubic.miny
                if not cubic.any_active_route_connecting((x, y), (x-1, y)):
                    self.draw_wall((xo, yo), (xo, yo+1))
                if not cubic.any_active_route_connecting((x, y), (x, y-1)):
                    self.draw_wall((xo, yo), (xo+1, yo))

        for feature in cubic.features:
            p0 = (feature.minx - cubic.minx,
                  feature.miny - cubic.miny)
            p1 = (1+feature.maxx - cubic.minx,
                  1+feature.maxy - cubic.miny)
            self.draw_feature(p0, p1, feature)

        return self.image


class BlockIllustratorBase(object):
    def __init__(self, junctions=[1], rooms=[0], xwalls=None, ywalls=None, xhalls=None, yhalls=None, margin=0):
        self.junctions = Choice.of(junctions)
        self.rooms = Choice.of(rooms)
        self.xwalls = Choice.of(xwalls or junctions)
        self.ywalls = Choice.of(ywalls or junctions)
        self.xhalls = Choice.of(xhalls or rooms)
        self.yhalls = Choice.of(yhalls or rooms)
        self.margin = margin

    def __call__(self, cubic):
        return self.draw(cubic)

    def draw(self, cubic):
        width = 1 + cubic.maxx - cubic.minx
        height = 1 + cubic.maxy - cubic.miny
        ox = cubic.minx
        oy = cubic.miny
        z = cubic.maxz
        if cubic.maxz != cubic.minz:
            raise RuntimeError('I can only draw 2D images')
        rows = [[None for _ in range(2*width+1)] for _ in range(2*height+1)]

        # Boundaries (left & top)
        for i in range(width):
            rows[0][i*2+1] = self.xwalls()
        for j in range(height):
            rows[j*2+1][0] = self.ywalls()

        # Junctions everywhere
        for i in range(width+1):
            for j in range(height+1):
                rows[j*2][i*2] = self.junctions()

        # Rooms and halls
        for i in range(width):
            x = ox + i
            for j in range(height):
                y = oy + j
                rows[j*2+1][i*2+1] = self.rooms()

                if cubic.any_active_route_connecting((x, y, z), (x+1, y, z)):
                    rows[j*2+1][i*2+2] = self.xhalls()
                else:
                    rows[j*2+1][i*2+2] = self.ywalls()

                if cubic.any_active_route_connecting((x, y, z), (x, y+1, z)):
                    rows[j*2+2][i*2+1] = self.yhalls()
                else:
                    rows[j*2+2][i*2+1] = self.xwalls()

        if self.margin:
            return [line[self.margin:-self.margin] for line in rows[self.margin:-self.margin]]
        else:
            return rows
