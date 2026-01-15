import yaml

class StaticLabel:
    key: str
    value: str

    def __init__(self, key, value):
        self.key = key
        self.value = value

class MetricLabelsConfig:
    static: list[StaticLabel]
    static_keys: list[str]
    static_values: list[str]

    def __init__(self, static):
        self.static = static
        self.static_keys = []
        self.static_values = []

        for s in static:
            self.static_keys.append(s.key)
            self.static_values.append(s.value)
            

class MetricConfig:
    scrape_interval_seconds: int
    namespace: str
    labels: MetricLabelsConfig

    def __init__(self, scrape_interval_seconds, namespace, labels):
        self.scrape_interval_seconds = scrape_interval_seconds
        self.namespace = namespace
        self.labels = labels

class ServerConfig:
    port: int
    certfile: str
    keyfile: str

    def __init__(self, port, certfile, keyfile):
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile

class Config:
    status_file: str
    server: ServerConfig
    metrics: MetricConfig

    def __init__(self, status_file, server, metrics):
        self.status_file = status_file
        self.server = server
        self.metrics = metrics


def load_config_from_file(config_file):
    with open(config_file, 'r') as file:
        config: dict = yaml.load(file, Loader=yaml.SafeLoader)

    server_config: dict = config['server']
    metric_config: dict = config['metrics']

    return Config(
        status_file= config['status_file'],
        server= ServerConfig(
            port= server_config.get('port'),
            certfile= server_config.get('certfile'),
            keyfile= server_config.get('keyfile')
        ),
        metrics= MetricConfig(
            scrape_interval_seconds= metric_config.get('scrape_interval_seconds'),
            namespace= metric_config.get('namespace'),
            labels= MetricLabelsConfig(
                static= convert_static_labels(metric_config['lables']['static'])
            )
        )
    )

def convert_static_labels(labels):
    converted = []
    if labels is not None:
        for label in labels:
            converted.append(StaticLabel(label['key'], label['value']))
    return converted