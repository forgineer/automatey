from automatey import Automatey


_automatey: Automatey = Automatey()
_automatey.logger.info("This is a log message from Automatey!")

if dag :=_automatey.get_config('automatey', 'dag'):
    _automatey.logger.info(f"DAG found: {dag}")

    tasks: list = dag.get('tasks', [])

    for task in tasks:
        _automatey.logger.info(f"Task found: {task}")
        