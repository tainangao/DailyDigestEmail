# DailyDigestEmail

Send curated email programmatically to recipients.

## Quick Start

Running this program locally

- Run `newsletter.py`, and an email will be sent to the recipients specified in the `.env` file, the file which is under the home directory.

Running this program on the Cloud

- Ideally this application should be hosted on the Cloud. An Airflow DAG should be built to run the job `@daily`.