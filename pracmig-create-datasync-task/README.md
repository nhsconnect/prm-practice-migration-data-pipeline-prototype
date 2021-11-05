## Create DataSync Task Lambda

### Prerequisites

- [pyenv](https://github.com/pyenv/pyenv#installation)
- Python 3.8.12 (installed with `pyenv`)
- `pipenv`: `pip install pipenv`
- Install dependencies: `pipenv install --dev`

### Running the tests

To run the tests from the CLI, first ensure your virtual environment is activated, e.g. with `pipenv shell`, and then run `pytest`.

### Deploy

` aws cloudformation create-stack --template-body "$(cat ./source-supplier.yml)" --capabilities CAPABILITY_NAMED_IAM --timeout-in-minutes 30 --stack-name "source-supplier-37" --disable-rollback`