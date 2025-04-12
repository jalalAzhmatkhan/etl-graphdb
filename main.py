import dask
from dask.distributed import Client

from services import etl_service
from settings import settings

def initialize_dask():
    """
    Initializes the Dask client and cluster.
    :return:
    """
    dask.config.set({'distributed.worker.resources.CPU': settings.DASK_CPU_LIMIT})
    if not settings.DASK_SCHEDULER_ADDRESS:
        print("[Main] Starting Dask Local Cluster")
        dask_local_cluster = dask.distributed.LocalCluster(
            dashboard_address=settings.DASK_DASHBOARD_PORT,
            n_workers=settings.N_WORKER_DASK,
            threads_per_worker=settings.N_THREADS_PER_DASK_WORKER,
            memory_limit=settings.DASK_MEMORY_LIMIT,
        )
        dask_client = Client(dask_local_cluster, timeout="60s")
        print(f"[Main] Dask dashboard on: {dask_client.dashboard_link}")
    else:
        dask_client = Client(
            settings.DASK_SCHEDULER_ADDRESS,
            timeout="60s",
            n_workers=settings.N_WORKER_DASK,
            threads_per_worker=settings.N_THREADS_PER_DASK_WORKER,
            memory_limit=settings.DASK_MEMORY_LIMIT
        )
        print(f"[Main] Dask dashboard on: {dask_client.dashboard_link}")

if __name__ == '__main__':
    initialize_dask()

    etl_service.create_pipeline(
        data_source_dir=settings.DATASOURCE_DIR,
        input_data_type='pdf',
        output_data_type='markdown',
        source_filename="BacNet_PointList_C1.pdf",
        output_dir=settings.OUTPUT_DIR,
        output_filename="bacnet_pointlist.md"
    )
