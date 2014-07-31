import os
from tito.common import *
from tito.builder.base import Builder
from tito.compat import *

class BrewDownloadBuilder(Builder):
    """
    A special case builder which uses pre-existing Brew builds and
    pulls down the resulting rpms locally. Useful in some cases when
    generating yum repositories during a release.
    """
    REQUIRED_ARGS = ['disttag']

    def __init__(self, name=None, tag=None, build_dir=None,
            config=None, user_config=None,
            args=None, **kwargs):

        Builder.__init__(self, name=name, tag=tag,
                build_dir=build_dir, config=config,
                user_config=user_config,
                args=args, **kwargs)

        self.dist_tag = args['disttag']

    def rpm(self):
        """
        Uses the SRPM
        Override the base builder rpm method.
        """

        print("Fetching rpms for %s.%s from brew:" % (
            self.build_tag, self.dist_tag))
        self._fetch_from_brew()

    def _fetch_from_brew(self):
        brew_nvr = "%s.%s" % (self.build_tag, self.dist_tag)
        debug("Brew NVR: %s" % brew_nvr)
        os.chdir(self.rpmbuild_dir)
        run_command("brew download-build %s" % brew_nvr)

        # Wipe out the src rpm for now:
        run_command("rm *.src.rpm")

        # Copy everything brew downloaded out to /tmp/tito:
        files = os.listdir(self.rpmbuild_dir)
        run_command("cp -v %s/*.rpm %s" %
                (self.rpmbuild_dir, self.rpmbuild_basedir))
        print
        print("Wrote:")
        for rpm in files:
            # Just incase anything slips into the build dir:
            if not rpm.endswith(".rpm"):
                continue
            rpm_path = os.path.join(self.rpmbuild_basedir, rpm)
            print("  %s" % rpm_path)
            self.artifacts.append(rpm_path)
        print
