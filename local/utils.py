import numpy as np

from enum import Enum, auto
from typing import Tuple, Dict

class Metric(Enum):
    DCR = auto()
    FEL = auto()
    FKGL = auto()
    FRE = auto()
    LLD = auto()
    LW = auto()
    MER = auto()
    RL = auto()

# Groupings for convenience
listenability_list: Tuple[Metric, ...] = (Metric.FEL, Metric.LLD, Metric.RL)
readability_list: Tuple[Metric, ...] = (
    Metric.DCR, Metric.FKGL, Metric.FRE, Metric.LW, Metric.MER
)

def every_other_label(bins):
    return tuple(str(x) if i % 2 == 0 else "" for i, x in enumerate(bins))

# All properties in one place for maintainability
METRIC_PROPERTIES: Dict[Metric, dict] = {
    Metric.DCR: {
        'bins': tuple(range(5, 14)),
        'xticks': tuple(range(5, 15, 2)),
        'yticks': np.linspace(0, 0.15, 4),
        'xticklabels': every_other_label(range(5, 14)),
        'title': "Dale–Chall Readability Formula",
    },
    Metric.FEL: {
        'bins': tuple(range(0, 21, 2)),
        'xticks': tuple(range(0, 21, 2)),
        'yticks': np.linspace(0, 0.075, 4),
        'xticklabels': every_other_label(range(0, 21, 2)),
        'title': "Fang's Easy Listening",
    },
    Metric.FRE: {
        'bins': (0, 10, 30, *range(50, 110, 10)),
        'xticks': tuple(range(0, 110, 10)),
        'yticks': np.linspace(0, 0.015, 4),
        'xticklabels': tuple(
            str(x) if x <= 30 or (i % 2 == 1) else ""
            for i, x in enumerate((0, 10, 30, *range(50, 110, 10)))
        ),
        'title': "Flesch Reading-Ease",
    },
    Metric.LLD: {
        'bins': tuple(range(0, 7)),
        'xticks': tuple(range(0, 7)),
        'yticks': np.linspace(0, 0.6, 4),
        'xticklabels': every_other_label(range(0, 7)),
        'title': "LLD",
    },
    Metric.LW: {
        'bins': tuple(range(30, 100, 10)),
        'xticks': tuple(range(30, 100, 10)),
        'yticks': np.linspace(0, 0.03, 4),
        'xticklabels': every_other_label(range(30, 100, 10)),
        'title': "Linsear Write",
    },
    Metric.MER: {
        'bins': (0, 21, 26, 30, 40),
        'xticks': tuple(range(0, 45, 5)),
        'yticks': np.linspace(0, 0.06, 4),
        'xticklabels': tuple(
            str(x) for i, x in enumerate((0, 21, 26, 30, 40))
        ),
        'title': "McAlpine EFLAW(TM) Readability",
    },
    Metric.RL: {
        'bins': tuple(range(0, 15, 2)),
        'xticks': tuple(range(0, 15, 2)),
        'yticks': np.linspace(0, 0.15, 4),
        'xticklabels': every_other_label(range(0, 15, 2)),
        'title': "Rogers' Listenability Formula",
    },
}

# Build maps from the properties
bins_map: Dict[Metric, Tuple[int, ...]] = {
    k: v['bins'] for k, v in METRIC_PROPERTIES.items() if v['bins']
}
boxplot_xtick_map: Dict[Metric, Tuple[int, ...]] = {
    k: v['xticks'] for k, v in METRIC_PROPERTIES.items() if v['xticks']
}
title_map: Dict[Metric, str] = {
    k: v['title'] for k, v in METRIC_PROPERTIES.items() if v['title']
}
ytick_map: Dict[Metric, Tuple[float, ...]] = {
    k: v['yticks'] 
    for k, v in METRIC_PROPERTIES.items() if v['yticks'].size > 0
}
xticklabels_map: Dict[Metric, Tuple[str, ...]] = {
    k: v['xticklabels'] 
    for k, v in METRIC_PROPERTIES.items() if v['xticklabels']
}

mapper_voa_level_to_color = {
    'beginner': "#009E73", 
    'intermediate': "#0072B2", 
    'advanced': "#D55E00", 
}

mapper_voa_transcript_to_color = {
    'actual': "#009E73", 
    'ka5': "#0072B2", 
    'gws': "#D55E00", 
}
