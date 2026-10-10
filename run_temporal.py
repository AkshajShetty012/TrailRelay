import asyncio
import sys
import uuid

from temporalio.client import Client
from temporalio.worker import Worker

from hello_workflow import HelloWorkflow

TASK_QUEUE = "trailrelay-test-queue"


async def main():
    client = await Client.connect("localhost:7233")

    if len(sys.argv) < 2 or sys.argv[1] not in ("worker", "start"):
        print("Usage: python run_temporal.py worker")
        print("   or: python run_temporal.py start")
        return

    if sys.argv[1] == "worker":
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[HelloWorkflow],
        )
        print("Temporal worker started. Waiting for workflows...")
        await worker.run()

    elif sys.argv[1] == "start":
        workflow_id = f"trailrelay-test-{uuid.uuid4()}"

        result = await client.execute_workflow(
            HelloWorkflow.run,
            "TrailRelay",
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )

        print(f"Workflow ID: {workflow_id}")
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
