
from datetime import timedelta

from temporalio import workflow

# Keep external activity imports outside the workflow sandbox.
with workflow.unsafe.imports_passed_through():
    from activities import classify_report


@workflow.defn
class TrailReportWorkflow:

    @workflow.run
    async def run(self, note: str) -> dict:
        report = await workflow.execute_activity(
            classify_report,
            note,
            start_to_close_timeout=timedelta(seconds=90),
        )

        return report
