from kubernetes import client, config
from adap.settings import Config
from .logging import get_logger
import time

log = get_logger(__name__)

namespace = Config.NAMESPACE
labels = {
    "app": "qa-perf-platform"
}

db_secret_name = 'db-conn-details'
kafka_secret_name = 'kafka-credentials'
slack_secret_name = 'slack-credentials'


def load_config():
    if Config.HOSTNAME.startswith('master0'):
        config.load_incluster_config()
    else:
        config.load_kube_config()


def authenticate(func):
    """ Decorator """
    def wrapper(*args, **kwargs):
        load_config()
        return func(*args, **kwargs)

    return wrapper


@authenticate
def verify_secret_exists(name):
    api_instance = client.CoreV1Api()
    try:
        api_instance.read_namespaced_secret(
            name=name,
            namespace=namespace)
        return True
    except client.rest.ApiException as e:
        if e.reason == 'Not Found':
            return False
        else:
            raise


def secret_env_source(name):
    secret_ref = client.V1SecretEnvSource(name=name)
    secret_env_src = client.V1EnvFromSource(secret_ref=secret_ref)
    return secret_env_src


# TODO: read_namespaced_secret requires permission to list secrets
# present_secrets = filter(
#     verify_secret_exists,
#     [db_secret_name, kafka_secret_name])
present_secrets = [db_secret_name, kafka_secret_name, slack_secret_name]
secret_env_sources = list(map(secret_env_source, present_secrets))


def wait_for_job_completion(job_name: str, max_wait: int, interval=60):
    log.info({
        'message': 'Wait for job to complete',
        'job_name': job_name,
        'max_wait': max_wait
        })
    _c = interval
    while _c < max_wait + 1:
        time.sleep(interval)
        load_config()
        log.debug(f"wait time: {_c}")
        job = client.BatchV1Api().read_namespaced_job_status(
            name=job_name,
            namespace=namespace)
        if job.status.active:
            _c += interval
            continue
        elif job.status.succeeded:
            log.info({
                'message': 'Job is complete',
                'job_name': job_name
                })
            break
        else:
            raise Exception(f"Job {job_name} failed: {job.status}")
    else:
        raise Exception(f"Max wait time for job {job_name} exceeded!")


@authenticate
def create_config_map(name: str, data: dict):
    log.debug(f"Creating configmap {name}: {data}")
    api_instance = client.CoreV1Api()

    cmap = client.V1ConfigMap()

    metadata = client.V1ObjectMeta(labels=labels)
    metadata.name = name
    cmap.metadata = metadata

    cmap.data = data

    api_instance.create_namespaced_config_map(namespace=namespace, body=cmap)


@authenticate
def create_job(job_name: str, command='python', args=[], cmap_data={}, cmap_name=''):
    """
    Create a kubernetes job.

    Either cmap_data OR cmap_name can be used.
    :param cmap_name: Name of an existing configmap
    :param cmap_data: Data for a new configmap
    """

    log.info({
        'message': 'Creating job',
        'job_name': job_name
        })
    api_instance = client.BatchV1Api()

    env_from_sources = secret_env_sources[:]

    if cmap_data:
        cmap_name = job_name
        create_config_map(name=cmap_name, data=cmap_data)
    if cmap_name:
        configMap = client.V1ConfigMapEnvSource(name=cmap_name)
        configMapRef = client.V1EnvFromSource(config_map_ref=configMap)
        env_from_sources.append(configMapRef)

    # Configureate Pod template container
    container = client.V1Container(
        name=job_name,
        image=Config.IMAGE,
        image_pull_policy='Always',
        command=[command],
        args=args,
        env_from=env_from_sources
        )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(name=job_name, labels=labels),
        spec=client.V1PodSpec(
            restart_policy="Never",
            termination_grace_period_seconds=30,
            containers=[container])
        )

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, labels=labels),
        spec=spec)

    api_instance.create_namespaced_job(
        body=job,
        namespace=namespace)


@authenticate
def deploy_locusts(suffix: str, cmap_data: dict, command='locust', **kwargs):
    """
    Distributed locust deployment, consisting of
        Service, Job (Master) and ReplicaSet (Slaves)

    Required Kwargs:
        filename (str): Path to locustfile (starting with 'adap')
        num_slaves (int): Number of locust slave replicas (pods)
        num_clients (int): Number of clients/workers total
        hatch_rate (float): Number of clients to be spun up per second
        run_time (str): Locust run time, e.g. '1h30m'
    Optional Kwargs:
        loglevel (str): Locust logging level. Default is INFO

    """

    filename = kwargs['filename']
    num_slaves = kwargs['num_slaves']
    num_clients = kwargs['num_clients']
    hatch_rate = kwargs['hatch_rate']
    run_time = kwargs['run_time']
    loglevel = kwargs.get('loglevel')

    master_name = f'locust-master-{suffix}'
    slave_name = f'locust-slave-{suffix}'

    master_args = [
        "-f", filename,
        "--master",
        f"--expect-slaves={num_slaves}",
        f"--clients={num_clients}",
        f"--hatch-rate={hatch_rate}",
        f"--run-time={run_time}",
        "--csv=/tmp/submit_judgments",
        "--only-summary", "--no-web",
        ]

    slave_args = [
        "-f", filename,
        "--slave",
        f"--master-host={master_name}"]

    log.info({
        'message': 'Deploying locust',
        'master_name': master_name,
        'run_time': run_time
        })

    if loglevel:
        arg = f"--loglevel={loglevel}"
        master_args.append(arg)
        slave_args.append(arg)

    # --------------------------   CREATE SERVICE   ---------------------

    api_instance = client.CoreV1Api()

    service = client.V1Service()
    service.api_version = "v1"
    service.kind = "Service"
    service_labels = labels.copy()
    service_labels.update({'role': master_name})
    service.metadata = client.V1ObjectMeta(
        name=master_name,
        labels=service_labels
        )
    selector = {'role': master_name}
    spec = client.V1ServiceSpec()
    spec.selector = selector
    spec.ports = [
        client.V1ServicePort(name="feeder", port=5555),
        client.V1ServicePort(name="workload", port=5556),
        client.V1ServicePort(name="communication", port=5557),
        client.V1ServicePort(name="communication-plus-1", port=5558),
        client.V1ServicePort(name="web-ui", port=8089, target_port=8089),
    ]
    service.spec = spec

    api_instance.create_namespaced_service(
        namespace=namespace,
        body=service)

    # --------------------------   CREATE LOCUST SLAVES   ---------------------

    api_instance = client.AppsV1Api()

    slave_cmap_data = cmap_data.copy()
    slave_cmap_defaults = {
        'LOG_TO_STDOUT': 'false',
        'LOG_HTTP': 'false',
        'FEEDER_HOST': master_name
    }
    for key, val in slave_cmap_defaults.items():
        if key not in slave_cmap_data:
            slave_cmap_data[key] = val

    create_config_map(name=slave_name, data=slave_cmap_data)
    slave_configMap = client.V1ConfigMapEnvSource(name=slave_name)
    slave_configMapRef = client.V1EnvFromSource(config_map_ref=slave_configMap)

    container = client.V1Container(
        name=slave_name,
        image=Config.IMAGE,
        image_pull_policy='Always',
        command=[command],
        args=slave_args,
        env_from=[*secret_env_sources, slave_configMapRef]
        )

    slave_labels = labels.copy()
    slave_labels.update({'role': slave_name})
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=slave_labels),
        spec=client.V1PodSpec(containers=[container])
        )

    # Create the specification
    spec = client.V1beta1ReplicaSetSpec(
        replicas=num_slaves,
        selector=client.V1LabelSelector(match_labels={'role': slave_name}),
        template=template
        )

    # Instantiate the replicaset object
    replicaset = client.V1beta1ReplicaSet(
        api_version='apps/v1',
        kind='ReplicaSet',
        metadata=client.V1ObjectMeta(name=slave_name, labels=labels),
        spec=spec
        )

    api_instance.create_namespaced_replica_set(
        namespace=namespace,
        body=replicaset)

    # # Create the specification
    # spec = client.AppsV1beta1DeploymentSpec(
    #     replicas=num_slaves,
    #     selector=client.V1LabelSelector(match_labels={'role': slave_name}),
    #     template=template
    #     )

    # # Instantiate the replicaset object
    # replicaset = client.AppsV1beta1Deployment(
    #     api_version='apps/v1',
    #     kind='Deployment',
    #     metadata=client.V1ObjectMeta(name=slave_name, labels=labels),
    #     spec=spec
    #     )

    # api_instance.create_namespaced_deployment(
    #     namespace=namespace,
    #     body=replicaset)

    # --------------------------   CREATE LOCUST MASTER   ---------------------

    api_instance = client.BatchV1Api()

    create_config_map(name=master_name, data=cmap_data)
    master_configMap = client.V1ConfigMapEnvSource(name=master_name)
    master_configMapRef = client.V1EnvFromSource(config_map_ref=master_configMap)

    # Configureate Pod template container
    container_ports = [
        client.V1ContainerPort(name='feeder', container_port=5555),
        client.V1ContainerPort(name="workload", container_port=5556),
        client.V1ContainerPort(name='comm', container_port=5557),
        client.V1ContainerPort(name='comm-plus-1', container_port=5558),
        client.V1ContainerPort(name='web-ui', container_port=8089),
    ]
    container = client.V1Container(
        name=master_name,
        image=Config.IMAGE,
        image_pull_policy='Always',
        command=[command],
        args=master_args,
        env_from=[*secret_env_sources, master_configMapRef],
        ports=container_ports
        )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(name=master_name, labels=service_labels),
        spec=client.V1PodSpec(
            restart_policy="Never",
            termination_grace_period_seconds=30,
            containers=[container])
        )

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=master_name, labels=service_labels),
        spec=spec)

    api_instance.create_namespaced_job(
        body=job,
        namespace=namespace)


@authenticate
def deploy_replicaset(**kwargs):
    """
    Deployment of a ReplicaSet

    Required Kwargs:
        num_replicas (int): Number of replicas (pods)
        name (str): A name for the replica set
        command (str): Command to be executed on each replica
        args (list): Arguments for the command
    Optional Kwargs:
        cmap_data (dict): Data for a config map
    """

    num_replicas = kwargs['num_replicas']
    name = kwargs['name']
    command = kwargs['command']
    args = kwargs['args']
    cmap_data = kwargs.get('cmap_data')

    api_instance = client.AppsV1Api()

    env_from_sources = [*secret_env_sources]
    if cmap_data:
        create_config_map(name=name, data=cmap_data)
        configMap = client.V1ConfigMapEnvSource(name=name)
        configMapRef = client.V1EnvFromSource(config_map_ref=configMap)
        env_from_sources.append(configMapRef)

    container = client.V1Container(
        name=name,
        image=Config.IMAGE,
        image_pull_policy='Always',
        command=[command],
        args=args,
        env_from=env_from_sources
        )

    rs_labels = labels.copy()
    rs_labels.update({'role': name})
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=rs_labels),
        spec=client.V1PodSpec(containers=[container])
        )

    # Create the specification
    spec = client.V1beta1ReplicaSetSpec(
        replicas=num_replicas,
        selector=client.V1LabelSelector(match_labels={'role': name}),
        template=template
        )

    # Instantiate the replicaset object
    replicaset = client.V1beta1ReplicaSet(
        api_version='apps/v1',
        kind='ReplicaSet',
        metadata=client.V1ObjectMeta(name=name, labels=labels),
        spec=spec
        )

    api_instance.create_namespaced_replica_set(
        namespace=namespace,
        body=replicaset)


def delete_labelled_pods(label: str):
    api_instance = client.CoreV1Api()
    pods = api_instance.list_namespaced_pod(
        namespace,
        label_selector=label)
    for pod in pods.items:
        name = pod.metadata.name
        log.debug(f"Deleting pod: {name}")
        api_instance.delete_namespaced_pod(
            name=name,
            namespace=namespace)


def delete_labelled_jobs(label: str):
    api_instance = client.BatchV1Api()
    jobs = api_instance.list_namespaced_job(
        namespace,
        label_selector=label)
    for job in jobs.items:
        name = job.metadata.name
        log.debug(f"Deleting job: {name}")
        api_instance.delete_namespaced_job(
            name=name,
            namespace=namespace)


def delete_labelled_services(label: str):
    api_instance = client.CoreV1Api()
    services = api_instance.list_namespaced_service(
        namespace,
        label_selector=label)
    for service in services.items:
        name = service.metadata.name
        log.debug(f"Deleting service: {name}")
        api_instance.delete_namespaced_service(
            name=name,
            namespace=namespace)


def delete_labeled_replicasets(label: str):
    api_instance = client.AppsV1Api()
    replicasets = api_instance.list_namespaced_replica_set(
        namespace,
        label_selector=label)
    for replicaset in replicasets.items:
        name = replicaset.metadata.name
        log.debug(f"Deleting replicaset: {name}")
        api_instance.delete_namespaced_replica_set(
            name=name,
            namespace=namespace)


def delete_labeled_configmaps(label: str):
    api_instance = client.CoreV1Api()
    cmaps = api_instance.list_namespaced_config_map(
        namespace,
        label_selector=label)
    for cmap in cmaps.items:
        name = cmap.metadata.name
        log.debug(f"Deleting configmap: {name}")
        api_instance.delete_namespaced_config_map(
            name=name,
            namespace=namespace)


@authenticate
def delete_all_labelled_resources(label=''):
    if not label:
        label = ",".join([f"{k}={v}" for k,v in labels.items()])
    log.info(f"Deleting all resources labelled {label}")
    delete_labelled_jobs(label)
    delete_labeled_replicasets(label)
    delete_labelled_pods(label)
    delete_labelled_services(label)
    delete_labeled_configmaps(label)
