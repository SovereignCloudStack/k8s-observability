import asyncio

from loguru import logger


async def ensure():
    for prerequisite in [
        ("kubectl", "version", "--client", "-ojson"),
        ("kind", "version"),
        ("helm", "version"),
        (
            "helm",
            "repo",
            "add",
            "prometheus-community",
            "https://prometheus-community.github.io/helm-charts",
        ),
        ("helm", "repo", "update", "prometheus-community"),
    ]:
        process = await asyncio.create_subprocess_exec(
            *prerequisite,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        resp, err = await process.communicate()
        if err:
            logger.error(err.decode())
            raise EnvironmentError

        logger.info(f"{' '.join(prerequisite)}\n{resp.decode()}")
