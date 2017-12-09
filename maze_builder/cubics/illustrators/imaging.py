from .base import BlockIllustratorBase, LineIllustratorBase
from PIL import Image, ImageDraw
import random
import zipfile


class ImageBlockIllustrator(BlockIllustratorBase):
    def __init__(self, wall_colors=[(0,0,0)], hall_colors=[(255,255,255)]):
        super().__init__(wall_colors, hall_colors)

    def __call__(self, cubic):
        return self.draw(cubic)

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

    def __call__(self, cubic):
        return self.draw(cubic)

    def draw(self, cubic):
        zoom = self.zoom if self.zoom else random.choice([1, 2, 3, 5, 8, 13, 21, 34, 55])
        tilt = self.tilt if self.tilt else random.random() * 360

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


class ZippedFeatures(object):
    def __init__(self, filename):
        self.filename = filename

    def __call__(self, width, height, background_color=None):
        return self.random_image(width, height, background_color)

    def random_image(self, width, height, background_color=None):
        background_color = background_color or (255, 255, 255)
        with zipfile.ZipFile(self.filename) as zf:
            name = random.choice(zf.namelist())
            of = zf.open(name)
            image = Image.open(of)
            image.load()
            if image.mode == 'P':
                image = image.convert('RGBA')
                image.load()
            if image.mode == 'RGBA':
                new_image = Image.new('RGB', image.size, background_color)
                new_image.paste(image, mask=image.split()[3])
                image = new_image
            image = image.resize((width, height), Image.BICUBIC)

            return image


class ImageLineIllustrator(LineIllustratorBase):
    def __init__(
        self,
        hall_width=1, wall_width=1,
        background_color=(255, 255, 255), wall_color=(0,0,0),
        features=None
    ):
        if isinstance(features, str) and features.endswith('.zip'):
            features = ZippedFeatures(features)
        self.features = features
        self.hall = hall_width
        self.wall = wall_width
        self.background_color = background_color
        self.wall_color = wall_color
        self.idraw = None

    def prepare(self, width, height):
        W = self.hall * width + self.wall * (width + 1)
        H = self.hall * height + self.wall * (height + 1)
        self.image = Image.new('RGB', (W, H), self.background_color)
        self.idraw = ImageDraw.Draw(self.image)

    def draw_wall(self, p0, p1):
        x0 = p0[0] * (self.hall + self.wall)
        y0 = p0[1] * (self.hall + self.wall)
        x1 = p1[0] * (self.hall + self.wall) + self.wall
        y1 = p1[1] * (self.hall + self.wall) + self.wall
        self.idraw.rectangle([x0, y0, x1, y1], self.wall_color)

    def draw_feature(self, p0, p1, feature):
        if not self.features:
            return
        x0 = (p0[0] + 1) * (self.hall + self.wall)
        y0 = (p0[1] + 1) * (self.hall + self.wall)
        x1 = (p1[0] - 1) * (self.hall + self.wall) + self.wall
        y1 = (p1[1] - 1) * (self.hall + self.wall) + self.wall

        fimage = self.features(x1-x0, y1-y0, self.background_color)
        self.image.paste(fimage, (x0, y0))
