from maze_builder.meshes.geometry import contains, BoundingBox


class StaticQuadTree(object):
    def __init__(self, objects, bbox=None, cell_limit=3, min_size=2, depth_limit=10):
        if bbox is None:
            bbox = BoundingBox.around(*objects)
        self.bbox = bbox
        self.cell_limit = cell_limit

        self.objects = ()
        self.children = ()

        objects = [obj for obj in objects if bbox.collides(obj, approximate=False)]
        if depth_limit <= 0 or len(objects) <= cell_limit or bbox.p1[0] - bbox.p0[0] <= min_size:
            self.objects = objects
        else:
            self.children = [
                self.__class__(objects, quadrant, cell_limit, min_size, depth_limit-1)
                for quadrant in bbox.split()
            ]

    def containers(self, point):
        if self.bbox.contains(point):
            for object in self.objects:
                if object.contains(point):
                    yield object
            if self.children:
                i = self.bbox.quadrant(point)
                yield from self.children[i].containers(point)

