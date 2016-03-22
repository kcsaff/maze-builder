from .base import BlockIllustratorBase
from PIL import Image
import random


class ImageBlockIllustrator(BlockIllustratorBase):
    def __init__(self, wall_colors=[(0,0,0)], hall_colors=[(255,255,255)]):
        super().__init__(wall_colors, hall_colors)

    def draw(self, cubic):
        data = super().draw(cubic)
        image = Image.new('RGB', (len(data[0]), len(data)))
        image.putdata(sum(data, []))
        return image


class ImageBlockIllustratorZoomed(BlockIllustratorBase):
    def __init__(self, wall_colors=[(0,0,0)], hall_colors=[(255,255,255)], zoom=None, tilt=None, size=None):
        super().__init__(wall_colors, hall_colors, margin=1)
        self.zoom = zoom
        self.tilt = tilt
        self.size = size

    def draw(self, cubic):
        zoom = self.zoom if self.zoom else random.choice([1, 2, 3, 5, 8, 13, 21, 34, 55])
        tilt = self.tilt if self.tilt else random.random() * 90

        data = super().draw(cubic)
        W, H = len(data[0]), len(data)
        size = self.size or (W, H)
        image = Image.new('RGB', (W, H))
        image.putdata(sum(data, []))

        m = min(W, H)
        M = max(W, H)

        if zoom != 1:
            image = image.crop((0, 0, m * 2 // zoom, m * 2 // zoom)).resize((M * 2, M * 2))
            image = image.rotate(tilt)
        ax, ay = image.size
        x0 = (ax - size[0]) // 2
        y0 = (ay - size[1]) // 2

        dest = Image.new('RGB', size)
        dest.paste(image.crop((x0, y0, x0+size[0], y0+size[1])))
        return dest
