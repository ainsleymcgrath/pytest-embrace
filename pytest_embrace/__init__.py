from __future__ import annotations

__version__ = "4.0.0"


from .case import CaseArtifact as CaseArtifact
from .case import derive_from_filename as derive_from_filename
from .case import trickles as trickles
from .codegen import RenderModuleBody as RenderModuleBody
from .codegen import RenderText as RenderText
from .embrace import Embrace as Embrace

# defining __all__ for the sake of generating docs with pdoc
__all__ = ["CaseArtifact", "derive_from_filename", "trickles", "Embrace"]
