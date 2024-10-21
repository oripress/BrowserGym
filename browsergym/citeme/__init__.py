from browsergym.core.registration import register_task
from browsergym.citeme.src import task

ALL_CM_TASK_IDS = []

# register a toy easy task for testing implemenation
gym_id = f"cm.imp.0"
register_task(
    gym_id,
    task.CiteMETask,
    task_kwargs={
        "task_id": f"imp.0",
        "output_file_path": "browsergym/citeme/predictions/imp.jsonl",
    },
)
ALL_CM_TASK_IDS.append(gym_id)

# register the CiteME dev set
for task_id in range(33):
    gym_id = f"cm.{task_id}"
    register_task(
        gym_id,
        task.CiteMETask,
        task_kwargs={"task_id": task_id},
    )
    ALL_CM_TASK_IDS.append(gym_id)

# register the CiteME test set
for task_id in range(181):
    gym_id = f"cm.test.{task_id}"
    register_task(
        gym_id,
        task.CiteMETask,
        task_kwargs={
            "task_id": f"test.{task_id}",
            "output_file_path": "browsergym/citeme/predictions/test.jsonl",
        },
    )
    ALL_CM_TASK_IDS.append(gym_id)