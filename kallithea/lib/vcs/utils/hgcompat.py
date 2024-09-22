"""
Mercurial libs compatibility
"""

import logging

import mercurial.encoding
import mercurial.localrepo


class MercurialStdLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        try:
            self.logger(message.decode().rstrip())
        except:
            self.logger(message)

    def flush(self):
        pass

def monkey_do():
    """Apply some Mercurial monkey patching"""
    # workaround for 3.3 94ac64bcf6fe and not calling largefiles reposetup correctly, and test_archival failing
    mercurial.localrepo.localrepository._lfstatuswriters = [lambda *msg, **opts: None]
    # 3.5 7699d3212994 added the invariant that repo.lfstatus must exist before hitting overridearchive
    mercurial.localrepo.localrepository.lfstatus = False

    # Minimize potential impact from custom configuration
    mercurial.encoding.environ[b'HGPLAIN'] = b'1'


hglog = logging.getLogger("mercurial")


def redirect_stdio_to_logging():
    # Capture Mercurial stdout/stderr and send to a 'mercurial' logger
    try:
        import mercurial.utils.procutil as procutil
        if not isinstance(procutil.stdout, MercurialStdLogger):
            procutil.stdout = MercurialStdLogger(hglog.info)
        if not isinstance(procutil.stderr, MercurialStdLogger):
            procutil.stderr = MercurialStdLogger(hglog.warning)
    except Exception as e:
        hglog.error("Exception installing procutil stdout/stderr: %s", e)
