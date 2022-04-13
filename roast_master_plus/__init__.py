import logging
import sys
from os.path import abspath, basename, exists, dirname, join

PROJECT_PATH = dirname(dirname(abspath(__file__)))
MANHOLE_PATH = join(PROJECT_PATH, "manhole-1.8.0-py2.py3-none-any.whl")

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    kw = {
        # 'format': '[%(asctime)s][%(pathname)s]: %(message)s',
        "format": "[%(asctime)s][%(module)s]: %(message)s",
        "datefmt": "%m/%d/%Y %H:%M:%S",
        "level": level,
        "stream": sys.stdout,
    }

    logging.basicConfig(**kw)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
        logging.WARNING
    )


def inject():
    """Inject a embedded server inside RoastMaster process so we can un-pickle its .dat format."""
    setup_logging()
    sys.path.append(MANHOLE_PATH)
    logger.info("injecting")
    import manhole

    manhole.install(
        verbose=True,
        verbose_destination=2,
        patch_fork=True,
        activate_on=None,
        oneshot_on=None,
        # sigmask=manhole.ALL_SIGNALS,
        socket_path=None,
        reinstall_delay=0.5,
        locals=None,
        strict=True,
    )
    logger.info("inject succesfull!")
