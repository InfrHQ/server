# Infr

An autonomous, open-source platform for data collection, storage, & retrieval that you can self-host.

![Infr](assets/images/infr.jpg)

## What is Infr?

Infr is a platform for data collection, storage, & retrieval that you can self-host. It is designed to be API-first & modular, so that you can easily add new data sources, storage backends, and retrieval methods.

## Why Infr?

Infr is built to be a open-source, API first & performant server which allows all your favourite apps & LLMs to personalise themselves to you.

## How does it work?

Infr server is a Python server that exposes a REST API to store, clean & query data. All actions are authorized by API keys, which can be generated by the Owner of the server. Once you share your API keys with your apps, they can start storing, querying & doing more with your data.

## Apps on Infr:

-   [Replay](https://meetreplay.com): An open-source, private webapp that allows you to remember everything you've ever seen on the internet.
-   [Infr Desktop Client](https://github.com/InfrHQ/desktop-client): An open-source, full-stack data collection app built for PCs, Mac & Linux systems

## Is there a hosted version?

Yes! We have a hosted version of Infr available at [getinfr.com](https://getinfr.com/register). You can sign up for free and start using it right away.

## How do I self-host?

Infr is currently in early development, and isn't expected as a drop-in replacement for existing items. However, if you want to try it out, you can follow the instructions below to get it running on your machine.

### Prerequisites

-   [Python 3.8 or above](https://www.python.org/downloads/)
-   [NodeJS 14 or above](https://nodejs.org/en/download/)
-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. Clone the repo

```bash
git clone https://github.com/InfrHQ/server.git
```

2. Run the setup script

```bash
python3 deployment.py --quickstart
```

4. Run the client available [here](https://github.com/InfrHQ/desktop-client)

## Development & Contributing

We welcome contributions from anyone and everyone. Please see our [contributing guide](CONTRIBUTING.md) for more info.

## Dashboard

The server comes with a simple dashboard to interact with the APIs. It is available at the "/" endpoint.
This index page only serves as a simple way to interact with the dashboard on the existing host.
The complete studio is available as a Tailwind & Next app in this [repo](https://github.com/InfrHQ/studio)

## Join the community

Join the community on [Discord](https://discord.gg/ZAejZCzaPe) to get help, discuss ideas, and contribute to the project.
Follow us on [Twitter](https://twitter.com/InfrHQ) to stay updated.