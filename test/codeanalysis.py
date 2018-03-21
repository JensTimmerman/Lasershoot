#/usr/bin/env python3
import pprint
from prospector.run import Prospector
from prospector.config import ProspectorConfig

from unittest import TestCase

import sys
import os

REPO_BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

class AnalyseTest(TestCase):
    """Testcase class that does code checking"""

    def test_prospector(self):
        """Run prospector tests"""

        PROSPECTOR_OPTIONS = [
            '--strictness', 'medium',
            '--max-line-length', '120',
            '--absolute-paths',
        ]
        sys.argv = ['fakename']
        sys.argv.extend(PROSPECTOR_OPTIONS)
        sys.argv.append(REPO_BASE_DIR)
        config = ProspectorConfig()
        prospector = Prospector(config)
        prospector.execute()
        failures = [msg.as_dict() for msg in prospector.get_messages()]
        self.assertFalse(failures, "prospector failures: %s" % pprint.pformat(failures))

    def _import(self, pkg):
        try:
            __import__(pkg)
        except ImportError as e:
            log.debug("__path__ %s",
                      ["%s = %s" % (name, getattr(mod, '__path__', 'None')) for name, mod in sys.modules.items()])
            self.assertFalse(e, msg="import %s failed sys.path %s exception %s" % (pkg, sys.path, e))

        self.assertTrue(pkg in sys.modules, msg='%s in sys.modules after import' % pkg)

    def test_import_packages(self):
        """Try to import each namespace"""
        res = {'packages': {}, 'modules': {}}
        offset = len(self.REPO_LIB_DIR.split(os.path.sep))
        for root, _, files in os.walk(self.REPO_LIB_DIR):
            package = '.'.join(root.split(os.path.sep)[offset:])
            if '__init__.py' in files or package in excluded_pkgs:
                # Force vsc shared packages/namespace
                if '__init__.py' in files and (package == 'vsc' or package.startswith('vsc.')):
                    init = open(os.path.join(root, '__init__.py')).read()
                    if not re.search(r'^import\s+pkg_resources\npkg_resources.declare_namespace\(__name__\)$',
                                     init, re.M):
                        raise Exception(('vsc namespace packages do not allow non-shared namespace in dir %s.'
                                         'Fix with pkg_resources.declare_namespace') % root)

                res['packages'][package] = self.rel_gitignore([os.path.join(root, f) for f in files])

                # this is a package, all .py files are modules
                for mod_fn in res['packages'][package]:
                    if not mod_fn.endswith('.py') or mod_fn.endswith('__init__.py'):
                        continue
                    modname = os.path.basename(mod_fn)[:-len('.py')]
                    res['modules']["%s.%s" % (package, modname)] = mod_fn

        for pkg in  res['packages']:
            self._import(pkg)
