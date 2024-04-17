# Merlin

[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/sotoon/merlin)](https://github.com/sotoon/merlin)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/sotoon/merlin)](https://github.com/sotoon/merlin/pulls)

## Overview

Merlin is Sotoon's Performance Management System.

## Table of Contents

- [Merlin](#merlin)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Running the project](#running-the-project)
  - [Documentation](#documentation)
  - [Contributing](#contributing)
  - [License](#license)

## Getting Started

### Prerequisites

To use the project you need to install these softwares: `python-3.11`, `node-20`, and `pnpm-8`

To install the dependencies of the project you can use:

```bash
make deps
```

For development you may need a localhost Postgres database with database name `merlin` nad username and passwords `postgres`. You can change this configuration in [development.py](merlin/settings/development.py).

To setup the environment variables in the project you can create `.env` files in the root of the project and also in the [frontend](frontend) directory. You can use these sample environment files: [sample.env](sample.env), [frontend/sample.env](frontend/sample.env)

### Running the project

To run the server on your localhost, First Make sure the environment is activated, then you can use:

```bash
make run-server
```

and to run the client:

```bash
make run-client
```

Also, you can use docker compose to run the project on docker compose. Just make sure to fix image urls(or use build) in docker compose file.

## Documentation

The project have two main components. The frontend part is based on `React` and `Material UI`. The backend part is based on `Django` and `Django Rest Framework`.

The settings and base configurations of the backend are located in the [merlin](merlin) directory. The backend logic is implemented in the [api](api) directory. By looking at the [api/models.py](api/models.py) You can understand the Model Structure of the project.

The code for the frontend of the project is also located in the [frontend](frontend) directory.

## Contributing

If you would like to contribute to the project, follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [BSD 3-Clause License](LICENSE).
