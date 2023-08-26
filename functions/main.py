# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import scheduler_fn, https_fn


@scheduler_fn.on_schedule(
    schedule="* * * * *",
    timezone=scheduler_fn.Timezone("America/Los_Angeles"),
)
def example(event: scheduler_fn.ScheduledEvent) -> None:
    print(event.job_name)
    print(event.schedule_time)


@https_fn.on_request()
def handle(request: https_fn.Request) -> https_fn.Response:
    return https_fn.Response(
        status_code=200,
        headers={"Content-Type": "text/plain"},
        body="Hello from Firebase!",
    )
