from maze_builder.random2 import weighted_choice, WeightedChoice


class BlockIllustratorBase(object):
    def __init__(self, junctions=[1], rooms=[0], xwalls=None, ywalls=None, xhalls=None, yhalls=None, margin=0):
        self.junctions = WeightedChoice.of(junctions)
        self.rooms = WeightedChoice.of(rooms)
        self.xwalls = WeightedChoice.of(xwalls or junctions)
        self.ywalls = WeightedChoice.of(ywalls or junctions)
        self.xhalls = WeightedChoice.of(xhalls or rooms)
        self.yhalls = WeightedChoice.of(yhalls or rooms)
        self.margin = margin

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
