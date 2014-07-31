# Import our builders so they can be referenced in config as tito.builder.Class
# regardless of which submodule they're in.

from tito.builder.base import Builder, NoTgzBuilder

from tito.builder.gembuilder import GemBuilder
from tito.builder.upstreambuilder import UpstreamBuilder, SatelliteBuilder
from tito.builder.mockbuilder import MockBuilder
from tito.builder.brewdownloadbuilder import BrewDownloadBuilder
from tito.builder.gitannexbuilder import GitAnnexBuilder
from tito.builder.fetch import FetchBuilder
from tito.builder.distributionbuilder import DistributionBuilder
