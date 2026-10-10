
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import classify_report, create_github_issue


@workflow.defn
class TrailReportWorkflow:

    @workflow.run
    async def run(self, note: str) -> dict:
        # Step 1: Classify the report locally using Gemma.
        report = await workflow.execute_activity(
            classify_report,
            note,
            start_to_close_timeout=timedelta(seconds=90),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
            ),
        )

        # Use a stable ID for duplicate detection during retries.
        report_id = workflow.info().workflow_id

        # Step 2: Send the classified report to GitHub.
        issue = await workflow.execute_activity(
            create_github_issue,
            args=[report_id, report],
            start_to_close_timeout=timedelta(seconds=45),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
        )

        return {
            "report": report,
            "github_issue": issue,
        }
