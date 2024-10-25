from playwright.sync_api import Page
from browsergym.core.task import AbstractBrowserTask
from browsergym.assistantbench.src.evaluation.evaluator import question_scorer
from browsergym.assistantbench.src.utils import add_prediction_to_jsonl
from datasets import load_dataset
from typing import Tuple, Dict

# Load dataset
DATA_DATASET = "bethgelab/CiteME"
all_tasks = load_dataset(DATA_DATASET, trust_remote_code=True)

# Filter the tasks by the given split name
def extract_data(split_name: str) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    split_tasks = [row for row in all_tasks if row["split"] == split_name]
    
    return (
        {str(i): row["excerpt"] for i, row in enumerate(split_tasks)},
        {str(i): row["target_paper_title"] for i, row in enumerate(split_tasks)},
        {str(i): row["id"] for i, row in enumerate(split_tasks)},
    )

# Implementation data for testing
def get_implementation_testing_data() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    return (
        {"imp.0": "20"},
        {
            "imp.0": "What is the weather in Paris yesterday in Celsius? Answer with the number only."
        },
        {"imp.0": "test_imp_id_0"},
    )


# Combine dev, test, and implementation-specific testing splits
gold_answers_train, tasks_train, ids_train = extract_data("train")
gold_answers_test, tasks_test, ids_test = extract_data("test")
gold_answers_impl_testing, tasks_test_impl_testing, ids_imp_testing = (
    get_implementation_testing_data()
)
gold_answers = {**gold_answers_train, **gold_answers_test, **gold_answers_impl_testing}
tasks = {**tasks_train, **tasks_test, **tasks_test_impl_testing}
ids = {**ids_train, **ids_test, **ids_imp_testing}


class CiteMETask(AbstractBrowserTask):

    @classmethod
    def get_task_id(cls) -> str:
        return f"ab.{cls.task_id}"

    def __init__(self, seed: int, task_id: str, output_file_path: str = None) -> None:
        """
        Args:
            seed (int): Random seed for task initialization.
            task_id (str): Unique identifier for the task (for the BrowserGym environment).
            output_file_path (str, optional): Path to the output file for saving results, needed for test set.
        """
        super().__init__(seed)
        self.task_id = task_id
        self.start_url = "https://www.semanticscholar.org/"
        self.goal = tasks[str(self.task_id)]
        self.gold = gold_answers[str(self.task_id)]
        self.ab_task_id = ids[self.task_id]
        self.output_file_path = output_file_path

    def setup(self, page: Page) -> Tuple[str, dict]:
        page.goto(self.start_url, timeout=10000)
        return self.goal, {}

    def teardown(self) -> None:
        pass

    def validate(self, page: Page, chat_messages: list[dict]) -> Tuple[float, bool, str, dict]:
        score, done, msg, info = 0.0, False, "", {}

        for i, message in enumerate(chat_messages):
            if (
                message.get("role") == "assistant" and i > 0
            ):  # eval when the agent returns a response
                done = True
                prediction = chat_messages[-1]["message"]
                score = question_scorer(prediction, self.gold)
                add_prediction_to_jsonl(
                    self.output_file_path, self.ab_task_id, prediction, True
                )  # save answer to file

        return score, done, msg, info