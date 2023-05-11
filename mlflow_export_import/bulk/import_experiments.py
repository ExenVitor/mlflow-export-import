""" 
Import a list of experiment from a directory.
"""

import os
from concurrent.futures import ThreadPoolExecutor
import click

import mlflow
from mlflow_export_import.common.click_options import (
    opt_input_dir, 
    opt_import_permissions,
    opt_import_source_tags,
    opt_use_src_user_id, 
    opt_experiment_rename_file,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.experiment.import_experiment import import_experiment
from mlflow_export_import.bulk import rename_utils

_logger = utils.getLogger(__name__)


def import_experiments(
        input_dir, 
        import_permissions = False,
        import_source_tags = False,
        use_src_user_id = False, 
        experiment_renames = None,
        use_threads = False,
        mlflow_client = None
    ): 
    experiment_renames = rename_utils.get_renames(experiment_renames)
    mlflow_client = mlflow_client or mlflow.MlflowClient()
    dct = io_utils.read_file_mlflow(os.path.join(input_dir, "experiments.json"))
    exps = dct["experiments"]
    _logger.info("Experiments:")
    for exp in exps:
        _logger.info(f"  {exp}")

    max_workers = utils.get_threads(use_threads)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for exp in exps:
            exp_input_dir = os.path.join(input_dir,exp["id"])
            exp_name = exp["name"]
            executor.submit(_import_experiment, mlflow_client, 
                exp_name, exp_input_dir, import_permissions, 
                import_source_tags, use_src_user_id, experiment_renames
            )


def _import_experiment(mlflow_client, exp_name, input_dir, import_permissions, 
         import_source_tags, use_src_user_id, experiment_renames
    ):
    try:
        exp_name =  rename_utils.rename(exp_name, experiment_renames, "experiment")
        import_experiment(
            mlflow_client = mlflow_client,
            experiment_name = exp_name,
            input_dir = input_dir,
            import_permissions = import_permissions,
            import_source_tags = import_source_tags,
            use_src_user_id = use_src_user_id
        )
    except Exception:
        import traceback
        traceback.print_exc()


@click.command()
@opt_input_dir
@opt_import_permissions
@opt_import_source_tags
@opt_use_src_user_id
@opt_experiment_rename_file
@opt_use_threads

def main(input_dir, import_permissions, import_source_tags, use_src_user_id, experiment_rename_file, use_threads): 
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_experiments(
        input_dir = input_dir, 
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        experiment_renames = experiment_rename_file,
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
