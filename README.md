# HUG Collaboration Project - Contribution of Semantic Annotations to the Quality of Internal Search

You can find some details in the [docs](docs) directory.

## Setup

Clone this repository
```bash
git clone https://github.com/ViktorooReps/hug-collab
```

Put the following necessary environment variables to `.env` file:
```yaml
USER_WEB=...
PASS_WEB=...
URL_WEB=...

USER_SOLR=...
PASS_SOLR=...
URL_SOLR=...
```

Set up Python virtual environment:
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```