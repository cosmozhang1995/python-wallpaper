class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def copy(self):
        return Point(x=self.x, y=self.y)
    def __str__(self):
        return "Point(%d,%d)" % (self.x, self.y)
    def __pos__(self):
        return Point(self.x, self.y)
    def __neg__(self):
        return Point(-self.x, -self.y)
    def __add__(self, other):
        if isinstance(other, Point): return Point(self.x + other.x, self.y + other.y)
        else: return Point(self.x + other, self.y + other)
    def __radd__(self, other):
        if isinstance(other, Point): return Point(self.x + other.x, self.y + other.y)
        else: return Point(self.x + other, self.y + other)
    def __sub__(self, other):
        if isinstance(other, Point): return Point(self.x - other.x, self.y - other.y)
        else: return Point(self.x - other, self.y - other)
    def __rsub__(self, other):
        if isinstance(other, Point): return Point(other.x - self.x, other.y - self.y)
        else: return Point(other - self.x, other - self.y)
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)
    def __rmul__(self, other):
        return Point(self.x * other, self.y * other)
    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)
    def __rtruediv__(self, other):
        return Point(other / self.x, other / self.y)

class Rect:
    def __init__(self, left=0, top=0, right=0, bottom=0, winapi_rect=None, qrect=None):
        if winapi_rect:
            self.left = winapi_rect[0]
            self.top = winapi_rect[1]
            self.right = winapi_rect[2]
            self.bottom = winapi_rect[3]
        elif qrect:
            self.left = qrect.left()
            self.right = qrect.right() + 1
            self.top = qrect.top()
            self.bottom = qrect.bottom() + 1
        else:
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom
    def copy(self):
        return Rect(left=self.left, top=self.top, right=self.right, bottom=self.bottom)
    def __str__(self):
        return "Rect(%d,%d,%d,%d)" % (self.left, self.top, self.right, self.bottom)
    def __eq__(self, other):
        if self.left != other.left: return False
        if self.top != other.top: return False
        if self.right != other.right: return False
        if self.bottom != other.bottom: return False
        return True
    # getter of computable properties
    @property
    def width(self):
        return self.right - self.left
    @property
    def height(self):
        return self.bottom - self.top
    @property
    def hcenter(self):
        return int((self.right + self.left) / 2)
    @property
    def vcenter(self):
        return int((self.bottom + self.top) / 2)
    # getter of corner points
    @property
    def lefttop(self):
        return Point(self.left, self.top)
    @property
    def topleft(self):
        return Point(self.left, self.top)
    @property
    def righttop(self):
        return Point(self.right, self.top)
    @property
    def topright(self):
        return Point(self.right, self.top)
    @property
    def leftbottom(self):
        return Point(self.left, self.bottom)
    @property
    def bottomleft(self):
        return Point(self.left, self.bottom)
    @property
    def rightbottom(self):
        return Point(self.right, self.bottom)
    @property
    def bottomright(self):
        return Point(self.right, self.bottom)
    # getter of center and edge centers
    @property
    def centerleft(self):
        return Point(self.left, vcenter)
    @property
    def leftcenter(self):
        return Point(self.left, vcenter)
    @property
    def centerright(self):
        return Point(self.right, vcenter)
    @property
    def rightcenter(self):
        return Point(self.right, vcenter)
    @property
    def centertop(self):
        return Point(self.hcenter, self.top)
    @property
    def topcenter(self):
        return Point(self.hcenter, self.top)
    @property
    def centerbottom(self):
        return Point(self.hcenter, self.bottom)
    @property
    def bottomcenter(self):
        return Point(self.hcenter, self.bottom)
    @property
    def center(self):
        return Point(self.hcenter, self.vcenter)
    # getter of area
    @property
    def area(self):
        return self.width * self.height
    # calculate overlap rectangal
    @classmethod
    def overlap(cls, rect1, rect2):
        newrect = Rect(left = max(rect1.left, rect2.left),
                       right = min(rect1.right, rect2.right),
                       top = max(rect1.top, rect2.top),
                       bottom = min(rect1.bottom, rect2.bottom))
        if newrect.width < 0 or newrect.height < 0:
            return None
        return newrect
    def __and__(self, other):
        return Rect.overlap(self, other)
    def __rand__(self, other):
        return Rect.overlap(self, other)

    
