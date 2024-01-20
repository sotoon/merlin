# Merlin

[![License](https://img.shields.io/badge/Licensce-GNU-blue)](LICENSE)
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
  - [Documentaion](#documentaion)
  - [Contributing](#contributing)
  - [License](#license)

## Getting Started

### Prerequisites

To use the project you need to install these softwares: `python-3.11`, `node-21.5.0`, and `npm-10.3.0`

To install the dependencies of the project you can use:

```bash
make deps
```

Also, to install the dependencies of the frontend of the project you can do:

```bash
cd frontend && npm i
```

### Running the project

To run the server on your localhost you can use:

```bash
make run-server
```

and to run the client:

```bash
make run-client
```

Also, you can use docker compose to run the project on docker compose. Just make sure to fix image urls(or use build) in docker compose file.

## Documentaion

The project have two main components. The frontend part is based on `React` and `Material UI`. The backend part is based on `Django` and `Django Rest Framework`.

## Contributing

If you would like to contribute to the project, follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.
