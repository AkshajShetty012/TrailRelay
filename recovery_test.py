from datetime import timedelta
from temporalio import workflow


@workflow.defn
class RecoveryTestWorkflow:

    @workflow.run
    async def run(self) -> str:
        await workflow.sleep(timedelta(seconds=60))
        return "Recovery test completed successfully."