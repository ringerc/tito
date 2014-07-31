import os
from tito.common import *
from tito.builder.base import NoTgzBuilder
from tito.compat import *

class GemBuilder(NoTgzBuilder):
    """
    Gem Builder

    Builder for packages whose sources are managed as gem source structures
    and the upstream project does not want to store gem files in git.
    """

    def _setup_sources(self):
        """
        Create a copy of the git source for the project at the point in time
        our build tag was created.

        Created in the temporary rpmbuild SOURCES directory.
        """
        self._create_build_dirs()

        debug("Creating %s from git tag: %s..." % (self.tgz_filename,
            self.git_commit_id))
        create_tgz(self.git_root, self.tgz_dir, self.git_commit_id,
                self.relative_project_dir,
                os.path.join(self.rpmbuild_sourcedir, self.tgz_filename))

        # Extract the source so we can get at the spec file, etc.
        debug("Copying git source to: %s" % self.rpmbuild_gitcopy)
        run_command("cd %s/ && tar xzf %s" % (self.rpmbuild_sourcedir,
            self.tgz_filename))

        # Find the gemspec
        gemspec_filename = find_gemspec_file(in_dir=self.rpmbuild_gitcopy)

        debug("Building gem: %s in %s" % (gemspec_filename,
            self.rpmbuild_gitcopy))
        # FIXME - this is ugly and should probably be handled better
        cmd = "gem_name=$(cd %s/ && gem build %s | awk '/File/ {print $2}'); \
            cp %s/$gem_name %s/" % (self.rpmbuild_gitcopy, gemspec_filename,
            self.rpmbuild_gitcopy, self.rpmbuild_sourcedir)

        run_command(cmd)

        # NOTE: The spec file we actually use is the one exported by git
        # archive into the temp build directory. This is done so we can
        # modify the version/release on the fly when building test rpms
        # that use a git SHA1 for their version.
        self.spec_file_name = find_spec_file(in_dir=self.rpmbuild_gitcopy)
        self.spec_file = os.path.join(
            self.rpmbuild_gitcopy, self.spec_file_name)
