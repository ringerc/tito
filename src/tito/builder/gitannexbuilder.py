import os
from tito.common import *
from tito.compat import *
from tito.release import *
from tito.builder.base import NoTgzBuilder

class GitAnnexBuilder(NoTgzBuilder):
    """
    Builder for packages with existing tarballs checked in using git-annex,
    e.g. referencing an external source (web remote).  This builder will
    "unlock" the source files to get the real contents, include them in the
    SRPM, then restore the automatic git-annex symlinks on completion.
    """

    def _setup_sources(self):
        super(GitAnnexBuilder, self)._setup_sources()

        old_cwd = os.getcwd()
        os.chdir(os.path.join(old_cwd, self.relative_project_dir))

        (status, output) = getstatusoutput("which git-annex")
        if status != 0:
            msg = "Please run 'yum install git-annex' as root."
            error_out('%s' % msg)

        run_command("git-annex lock")
        annexed_files = run_command("git-annex find --include='*'").splitlines()
        run_command("git-annex get")
        run_command("git-annex unlock")
        debug("  Annex files: %s" % annexed_files)

        for annex in annexed_files:
            debug("Copying unlocked file %s" % annex)
            os.remove(os.path.join(self.rpmbuild_gitcopy, annex))
            shutil.copy(annex, self.rpmbuild_gitcopy)

        os.chdir(old_cwd)

    def cleanup(self):
        if self._lock_force_supported(self._get_annex_version()):
            run_command("git-annex lock --force")
        else:
            run_command("git-annex lock")
        super(GitAnnexBuilder, self).cleanup()

    def _get_annex_version(self):
        # git-annex needs to support --force when locking files.
        ga_version = run_command('git-annex version').split('\n')
        if ga_version[0].startswith('git-annex version'):
            return ga_version[0].split()[-1]
        else:
            return 0

    def _lock_force_supported(self, version):
        return compare_version(version, '5.20131213') >= 0
