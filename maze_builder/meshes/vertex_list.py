from array import array
import collections


class VertexList(object):
    def __init__(self, vertices=None, dims=0, ndigits=4, typecode='d', cache=1024, vertex_class=tuple):
        self.dims = dims
        self.ndigits = ndigits
        self.data = array(typecode)
        self.cache = LruDict(cache)
        self.vertex_class = vertex_class
        if vertices:
            self.extend(vertices, share=False)

    def __len__(self):
        return len(self.data) // self.dims if self.dims else 0

    def __getitem__(self, item):
        if isinstance(item, slice):
            return tuple(self[i] for i in range(*item.indices(len(self))))
        else:
            di = item * self.dims
            return self._rounded(self.data[di:di+self.dims])

    def __iter__(self):
        for di in range(0, self.dims * len(self), self.dims):
            yield self._rounded(self.data[di:di+self.dims])
            
    def __setitem__(self, key, value):
        if not (0 <= key < len(self)):
            raise IndexError('Index {} is out of range (0, {})'.format(key, len(self)))
        self._check(value)

        old_rounded_value = self[key]
        rounded_value = self._rounded(value)
        if old_rounded_value == rounded_value:
            return
        old_h = hash(old_rounded_value)
        self.cache.pop(old_h)
        h = hash(rounded_value)
        self.cache[h] = key
        for i, c in enumerate(value, key * self.dims):
            self.data[i] = c

    def warp(self, warp):
        self.cache.clear()
        for di in range(0, self.dims * len(self), self.dims):
            warped = warp(self.vertex_class(self.data[di:di+self.dims]))
            for i, c in enumerate(warped, di):
                self.data[i] = c

    def warped(self, warp):
        result = self._similar_list()
        for di in range(0, self.dims * len(self), self.dims):
            warped = warp(self.vertex_class(self.data[di:di+self.dims]))
            result.append(warped, share=False)
        return result

    def append(self, vertex, share=True):
        self._check(vertex)
        rounded_vertex = self._rounded(vertex)

        h = hash(rounded_vertex)
        index = self.cache.get(h) if share else None
        if index is None or self[index] != rounded_vertex:
            index = len(self)
            self.cache[h] = index
            self.data.extend(vertex)
        return index
    
    def extend(self, vertices, share=True):
        if share:
            return [self.append(v, share=True) for v in vertices]
        else:
            start = len(self)
            for v in vertices:
                self.append(v, share=False)
            stop = len(self)
            return range(start, stop)

    # Internal

    def _similar_list(self):
        cls = self.__class__
        return cls(
            ndigits=self.ndigits, typecode=self.data.typecode,
            cache=self.cache.maxlen, vertex_class=self.vertex_class
        )

    def _check(self, vertex):
        if not self.dims:
            self.dims = len(vertex)
        elif len(vertex) != self.dims:
            raise RuntimeError('Vertex must be {}D for this vertex list'.format(self.dims))

    def _rounded(self, vertex):
        return self.vertex_class(round(c, self.ndigits) for c in vertex)


class LruDict(collections.MutableMapping):
    # http://stackoverflow.com/a/2438926/1115497
    def __init__(self, maxlen, *a, **k):
        self.maxlen = maxlen
        self.d = dict(*a, **k)
        while len(self) > maxlen:
            self.popitem()

    def __iter__(self):
        return iter(self.d)

    def __len__(self):
        return len(self.d)

    def __getitem__(self, k):
        return self.d[k]

    def __delitem__(self, k):
        del self.d[k]

    def __setitem__(self, k, v):
        if k not in self and len(self) == self.maxlen:
            self.popitem()
        self.d[k] = v

