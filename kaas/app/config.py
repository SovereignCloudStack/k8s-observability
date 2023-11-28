from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLITE_DATABASE_PATH: str = "./kaas.db"
    KAAS_MAX_CLUSTERS: int = 4
    KAAS_HOST: str = ""
    KAAS_IMAGE: str = "kindest/node:v1.25.11"
    KAAS_CONFIG: str = "./manifests/kind-config.yaml"
    KAAS_MONITORING_CONFIG: str = "./manifests/kaas-monitoring-values.yaml"
    OBSERVER_KUBECONFIG: str = "./manifests/observer-kubeconfig.yaml"
    OBSERVER_REMOTE_WRITE_URL: str = "http://observer-control-plane:30291/api/v1/receive"

    class Config:
        env_file = "./.env"


settings = Settings()
