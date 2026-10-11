from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from temporalio.client import Client

from trail_workflow import TrailReportWorkflow


app = FastAPI(title="TrailRelay API")

TASK_QUEUE = "trailrelay-queue"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://0.0.0.0:5500",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class ReportPayload(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    note: str = Field(min_length=1, max_length=1000)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reports")
async def submit_report(report: ReportPayload):
    client = await Client.connect("localhost:7233")

    workflow_id = f"trail-report-{report.id}"

    result = await client.execute_workflow(
        TrailReportWorkflow.run,
        report.note.strip(),
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    return {
        "status": "processed",
        "workflow_id": workflow_id,
        "result": result,
    }
