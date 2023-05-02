from math import nan
from manim import WHITE, Scene, tempconfig, Mobject
from custom_json import custom_dump, custom_parse
from lamination import Lamination
from points import FloatWrapper, NaryFraction, UnitPoint
from typing import Tuple, Union
from animation import AnimateLamination, lerp


def remove_occluded(
    ret: Lamination, occlusion: Tuple[NaryFraction, NaryFraction]
) -> Lamination:
    def criteria(point):
        return (
            point.to_float() < occlusion[0].to_float()
            or point.to_float() > occlusion[1].to_float()
        )

    ret.points = list(filter(criteria, ret.points))
    ret.polygons = list(filter(lambda polly: criteria(polly[0]), ret.polygons))
    return ret


def morph_function(x: float, occlusion: Tuple[UnitPoint, UnitPoint]) -> float:
    a, b = occlusion[0].to_float(), occlusion[1].to_float()
    bite_length = b - a
    remaining_length = 1 - bite_length
    # Calculate the midpoint of the range
    midpoint = (a + b) / 2
    # Calculate the opposite of the midpoint
    opposite = midpoint + 0.5 if midpoint < 0.5 else midpoint - 0.5

    # Determine which side of the midpoint the angle is on
    if x >= a and x <= b:
        # The angle is in the range, so map it to the midpoint
        return midpoint
    elif x < a:
        # The angle is below the range, so stretch the lower half of the circle
        return ((x - opposite) / remaining_length) + opposite
    else:
        # The angle is above the range, so stretch the upper half of the circle
        return ((x - b) / remaining_length) + midpoint


def result(lam: Lamination) -> Lamination:
    def mapping(p: UnitPoint) -> UnitPoint:
        assert lam.occlusion is not None
        return FloatWrapper(morph_function(p.to_float(), lam.occlusion))

    return lam.apply_function(mapping)


class MorphOcclusion(AnimateLamination):
    def __init__(
        self,
        initial: Lamination,
        occlusion: Tuple[NaryFraction, NaryFraction],
        start_mobject: Union[Mobject, None] = None,
        **kwargs,
    ) -> None:
        initial.occlusion = occlusion
        reported_initial = remove_occluded(initial, occlusion)
        reported_final = result(initial)
        super().__init__(reported_initial, reported_final, **kwargs)


class MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        initial = custom_parse(
            """{
        "polygons": [["0_003", "0_030", "0_300"],
          ["1_003", "3_030", "3_300"],
          ["2_003", "2_030", "2_300"],
          ["3_003", "1_030", "1_300"]],
        "chords": [],
        "points": [],
        "radix": 4}"""
        )
        assert isinstance(initial, Lamination)
        occlusion = (initial.polygons[0][0], initial.polygons[0][2])
        self.play(MorphOcclusion(initial, occlusion, run_time=5))


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = MyScene()
        scene.render()
