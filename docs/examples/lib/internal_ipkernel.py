#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import subprocess
import sys

from IPython.zmq.ipkernel import IPKernelApp

#-----------------------------------------------------------------------------
# Functions and classes
#-----------------------------------------------------------------------------
def pylab_kernel(gui):
    """Launch and return an IPython kernel with pylab support for the desired gui
    """
    kernel = IPKernelApp()
    # FIXME: we're hardcoding the heartbeat port b/c of a bug in IPython 0.11
    # that will set it to 0 if not specified.  Once this is fixed, the --hb
    # parameter can be omitted and all ports will be automatic
    kernel.initialize(['python', '--pylab=%s' % gui, '--hb=19999',
                       #'--log-level=10'
                       ])
    return kernel


def qtconsole_cmd(kernel):
    """Compute the command to connect a qt console to an already running kernel
    """
    ports = ['--%s=%d' % (name, port) for name, port in kernel.ports.items()]
    return ['ipython', 'qtconsole', '--existing'] + ports


class InternalIPKernel(object):

    def init_ipkernel(self, backend):
        # Start IPython kernel with GUI event loop and pylab support
        self.ipkernel = pylab_kernel(backend)
        # To create and track active qt consoles
        self._qtconsole_cmd = qtconsole_cmd(self.ipkernel)
        self.consoles = []
        
        # This application will also act on the shell user namespace
        self.namespace = self.ipkernel.shell.user_ns
        # Keys present at startup so we don't print the entire pylab/numpy
        # namespace when the user clicks the 'namespace' button
        self._init_keys = set(self.namespace.keys())

        # Example: a variable that will be seen by the user in the shell, and
        # that the GUI modifies (the 'Counter++' button increments it):
        self.namespace['app_counter'] = 0
        #self.namespace['ipkernel'] = self.ipkernel  # dbg

    def print_namespace(self, evt=None):
        print "\n***Variables in User namespace***"
        for k, v in self.namespace.iteritems():
            if k not in self._init_keys and not k.startswith('_'):
                print '%s -> %r' % (k, v)
        sys.stdout.flush()

    def new_qt_console(self, evt=None):
        self.consoles.append(subprocess.Popen(self._qtconsole_cmd))

    def count(self, evt=None):
        self.namespace['app_counter'] += 1

    def cleanup_consoles(self, evt=None):
        for c in self.consoles:
            c.kill()
