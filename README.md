NovaMart is a fictional retail company that uses data engineering systems to solve business problems and support informed decision-making.
This repository contains data pipelines that collect, validate, transform, and prepare customer, product, order, and sales data for analysis, reporting, and visualization.

## Prerequisites

* Git
* Python
* PostgreSQL
* Visual Studio Code

## Local Setup

Clone the repository:

```bat
git clone https://github.com/2sammy/novamart-data-platform.git
```

Enter the project directory:

```bat
cd novamart-data-platform
```

### Python Environment Setup

Create and activate the virtual environment, install dependencies, and run the tests:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pytest
```
