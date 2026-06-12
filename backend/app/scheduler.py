"""
Scheduler de probes automatiques.

Lance un AsyncIOScheduler qui appelle periodiquement la fonction de
monitoring des sites, sans dependance a un appel HTTP externe.

Activable / desactivable via la variable d'environnement
SCHEDULER_ENABLED (defaut: true).
"""
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Intervalle de probe en secondes (par defaut: 30 s)
PROBE_INTERVAL_SECONDS = int(os.getenv("PROBE_INTERVAL_SECONDS", "30"))
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() in ("true", "1", "yes")


def start_scheduler(probe_function) -> AsyncIOScheduler | None:
    """Demarre un scheduler asyncio qui execute probe_function periodiquement."""
    if not SCHEDULER_ENABLED:
        logger.info("scheduler_disabled_by_env")
        return None

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        probe_function,
        trigger=IntervalTrigger(seconds=PROBE_INTERVAL_SECONDS),
        id="auto_monitor_probes",
        name="Probes HTTP automatiques",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=10,
    )
    scheduler.start()
    logger.info(
        "scheduler_started",
        extra={"interval_seconds": PROBE_INTERVAL_SECONDS},
    )
    return scheduler
