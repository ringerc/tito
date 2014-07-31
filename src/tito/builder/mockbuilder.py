import os
from tito.common import *
from tito.compat import *
from tito.release import *
from tito.builder.base import Builder

class MockBuilder(Builder):
    """
    Uses the mock tool to create a chroot for building packages for a different
    OS version than you may be currently using.
    """
    REQUIRED_ARGS = ['mock']

    def __init__(self, name=None, tag=None, build_dir=None,
            config=None, user_config=None,
            args=None, **kwargs):

        # Mock builders need to use the packages normally configured builder
        # to get at a proper SRPM:
        self.normal_builder = create_builder(name, tag, config,
                build_dir, user_config, args, **kwargs)

        Builder.__init__(self, name=name, tag=tag,
                build_dir=build_dir, config=config,
                user_config=user_config,
                args=args, **kwargs)

        self.mock_tag = args['mock']
        self.mock_cmd_args = ""
        if 'mock_config_dir' in args:
            mock_config_dir = args['mock_config_dir']
            if not mock_config_dir.startswith("/"):
                # If not an absolute path, assume below git root:
                mock_config_dir = os.path.join(self.git_root, mock_config_dir)
            if not os.path.exists(mock_config_dir):
                raise TitoException("No such mock config dir: %s" % mock_config_dir)
            self.mock_cmd_args = "%s --configdir=%s" % (self.mock_cmd_args, mock_config_dir)

        # Optional argument which will skip mock --init and add --no-clean
        # and --no-cleanup-after:
        self.speedup = False
        if 'speedup' in args:
            self.speedup = True
            self.mock_cmd_args = "%s --no-clean --no-cleanup-after" % \
                    (self.mock_cmd_args)

        if 'mock_args' in args:
            self.mock_cmd_args = "%s %s" % (self.mock_cmd_args, args['mock_args'])

        # TODO: error out if mock package is not installed

        # TODO: error out if user does not have mock group

    def srpm(self, dist=None):
        """
        Build a source RPM.

        MockBuilder will use an instance of the normal builder for a package
        internally just so we can generate a SRPM correctly before we pass it
        into mock.
        """
        self.normal_builder.srpm(dist)
        self.srpm_location = self.normal_builder.srpm_location
        self.artifacts.append(self.srpm_location)

    def rpm(self):
        """
        Uses the SRPM
        Override the base builder rpm method.
        """

        print("Creating rpms for %s-%s in mock: %s" % (
            self.project_name, self.display_version, self.mock_tag))
        if not self.srpm_location:
            self.srpm()
        print("Using srpm: %s" % self.srpm_location)
        self._build_in_mock()

    def _build_in_mock(self):
        if not self.speedup:
            print("Initializing mock...")
            output = run_command("mock %s -r %s --init" % (self.mock_cmd_args, self.mock_tag))
        else:
            print("Skipping mock --init due to speedup option.")

        print("Installing deps in mock...")
        output = run_command("mock %s -r %s %s" % (
            self.mock_cmd_args, self.mock_tag, self.srpm_location))
        print("Building RPMs in mock...")
        output = run_command('mock %s -r %s --rebuild %s' %
                (self.mock_cmd_args, self.mock_tag, self.srpm_location))
        mock_output_dir = os.path.join(self.rpmbuild_dir, "mockoutput")
        output = run_command("mock %s -r %s --copyout /builddir/build/RPMS/ %s" %
                (self.mock_cmd_args, self.mock_tag, mock_output_dir))

        # Copy everything mock wrote out to /tmp/tito:
        files = os.listdir(mock_output_dir)
        run_command("cp -v %s/*.rpm %s" %
                (mock_output_dir, self.rpmbuild_basedir))
        print
        print("Wrote:")
        for rpm in files:
            rpm_path = os.path.join(self.rpmbuild_basedir, rpm)
            print("  %s" % rpm_path)
            self.artifacts.append(rpm_path)
        print

