from copy import copy
from math import ceil

pxl_base = 64

# Ratio configuration
ratios = {
    "Custom": None,
    "1:1": {"SD 1.5": 1024 / 2, "SDXL": 1024},
    "2:3": {"SD 1.5": 418 / 2, "SDXL": 418},
    "4:5": {"SD 1.5": 228.75 / 2, "SDXL": 228.75},
    "4:7": {"SD 1.5": 192 / 2, "SDXL": 192},
    "5:12": {"SD 1.5": 128 / 2, "SDXL": 128},
    "7:9": {"SD 1.5": 128 / 2, "SDXL": 128},
    "9:16": {"SD 1.5": 60, "SDXL": 90},
    "9:21": {"SD 1.5": (670 / 9) / 2, "SDXL": 670 / 9},
    "13:19": {"SD 1.5": 32, "SDXL": 64},
}
str_ratios = list(ratios.keys())

# SDXL Dimensions
sdxl_dimensions = [
    "1024 x 1024",
    "896 x 1152",  # 7:9
    "832 x 1216",  # 13:19
    "768 x 1344",  # 4:7
    "640 x 1536",  # 5:12
    "1216 x 832",
]

# WAN Dimensions (original max 832)
wan_dimensions = [
    "480 x 832",  # vertical long
    "512 x 512",  # square
    "496 x 640",  # vertical short
    "640 x 496",  # horizontal short
    "832 x 480",  # horizontal long
    "496 x 660",  # vertical short2
    "660 x 496",  # horizontal short2
    "480 x 580",  # vertical almost square
    "580 x 480",  # horizontal almost square
]

# WAN Dimensions 720/1280 (Scaled up to max 1280, incorporating 9:16 ratio)
# The dimensions are scaled by approx 1.5x and adjusted to be multiples of 8.
wan_dimensions_720 = [
    "720 x 1280",  # vertical long (9:16)
    "768 x 768",   # square (scaled from 512x512)
    "744 x 960",   # vertical short (scaled from 496x640)
    "960 x 744",   # horizontal short
    "1280 x 720",  # horizontal long (16:9)
    "744 x 992",   # vertical short2 (scaled from 496x660)
    "992 x 744",   # horizontal short2
    "720 x 870",  # vertical almost square
    "870 x 720",  # horizontal almost square
]


def apply_ratio(width, height, ratio, enforce_width: bool = True, swapped: bool = False):
    r_width, r_height = ratio
    if enforce_width:
        factor = width // r_width
        return (width, (factor * r_height)) if not swapped else ((factor * r_height), width)
    else:
        factor = height // r_height
        return ((factor * r_width), height) if not swapped else (height, (factor * r_width))


def apply_pure_ratio(ratio, ratio_scale: float = 1.0, swapped: bool = False):
    r_width, r_height = ratio
    ratioed_width = int(r_width * pxl_base * ratio_scale)
    ratioed_height = int(r_height * pxl_base * ratio_scale)
    return (ratioed_height, ratioed_width) if swapped else (ratioed_width, ratioed_height)


class SDXLDimensions_simple:
    # This class seems to be the one using 'sdxl_dimensions'
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dimensions": (sdxl_dimensions,),
                "order": (["default (width,height)", "swapped (height,width)"],),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "better_dimensions"
    CATEGORY = "BetterDimensions"

    def better_dimensions(self, dimensions: str = "", order: str = ""):
        return tuple([int(dim) for dim in dimensions.split(" x ")[::-1 if order == "swapped (height,width)" else 1]])


class SDXLDimensions:
    # This class seems to be the one using 'wan_dimensions' (the original list)
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dimensions": (wan_dimensions,),
                "order": (["default (width,height)", "swapped (height,width)"],),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "better_dimensions"
    CATEGORY = "BetterDimensions"

    def better_dimensions(self, dimensions: str = "", order: str = ""):
        return tuple([int(dim) for dim in dimensions.split(" x ")[::-1 if order == "swapped (height,width)" else 1]])


class WANDimensions_720:
    # New class for wan_dimensions_720 list
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dimensions": (wan_dimensions_720,),
                "order": (["default (width,height)", "swapped (height,width)"],),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "better_dimensions"
    CATEGORY = "BetterDimensions"

    def better_dimensions(self, dimensions: str = "", order: str = ""):
        # Reuses the exact same dimension parsing logic
        return tuple([int(dim) for dim in dimensions.split(" x ")[::-1 if order == "swapped (height,width)" else 1]])


class PureRatio:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ratio": (str_ratios[1:],),
                "adjust_scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001,
                    "display": "number",
                }),
                "model": (["SDXL", "SD 1.5"],),
                "order": (["default (width,height)", "swapped (height,width)"],),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "better_dimensions"
    CATEGORY = "BetterDimensions"

    def better_dimensions(self, ratio: str = "", adjust_scale: float = 1.0, model: str = "", order: str = ""):
        swapped = order == "swapped (height,width)"
        builtin_scale = ratios[ratio][model]
        width, height = tuple([ceil(int(dim) * builtin_scale * adjust_scale) for dim in ratio.split(":")])
        return (width, height) if not swapped else (height, width)


class BetterDimensions:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 64, "max": 2 ** 20, "step": 2}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 2 ** 20, "step": 2}),
                "ratio": (str_ratios,),
                "enforce_dimension": (["width", "height"],),
                "order": (["default (width,height)", "swapped (height,width)"],),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "better_dimensions"
    CATEGORY = "BetterDimensions"

    def better_dimensions(self, width: int = 0, height: int = 0, ratio: str = "None", enforce_dimension: str = "width",
                          order: str = "default (width,height)"):
        swapped = order == "swapped (height,width)"
        w = copy(width) if width > 0 else 64
        h = copy(height) if height > 0 else 64
        if ratio == str_ratios[0]:  # Custom
            return (h, w) if swapped else (w, h)

        tuple_ratio = tuple([int(r) for r in ratio.split(":")])
        enforce_width = enforce_dimension == "width"
        return apply_ratio(w, h, tuple_ratio, enforce_width=enforce_width, swapped=swapped)


# Register the nodes with custom names
NODE_CLASS_MAPPINGS = {
    "BetterImageDimensions": BetterDimensions,
    "PureRatio": PureRatio,
    "SDXLDimensions_simple": SDXLDimensions_simple,
    "SDXLDimensions": SDXLDimensions,
    "WANDimensions_720": WANDimensions_720, # The new node class
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BetterImageDimensions": "Better Image Dimensions",
    "PureRatio": "Dimensions by Ratio",
    "SDXLDimensions_simple": "sdxl Dimensions",
    "SDXLDimensions": "wan Dimensions",
    "WANDimensions_720": "wan Dimensions 720", # The new node display name
}
