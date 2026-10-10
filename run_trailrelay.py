
import asyncio
import sys
import uuid

from temporalio.client import Client
from temporalio.worker import Worker

from trail_workflow import TrailReportWorkflow
from activities import classify_report


TASK_QUEUE = "trailrelay-queue"


async def main():
    client = await Client.connect("localhost:7233")

    if len(sys.argv) < 2:
        print('Usage: python run_trailrelay.py worker')
        print('   or: python run_trailrelay.py start "your report"')
        return

    command = sys.argv[1]

    if command == "worker":
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[TrailReportWorkflow],
            activities=[classify_report],
        )

        print("TrailRelay worker started.")
        await worker.run()

    elif command == "start":
        if len(sys.argv) < 3:
            print('Provide a report in quotes.')
            return

        note = " ".join(sys.argv[2:])
        workflow_id = f"trail-report-{uuid.uuid4()}"

        result = await client.execute_workflow(
            TrailReportWorkflow.run,
            note,
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )

        print(f"\nWorkflow ID: {workflow_id}")
        print("Classified report:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
