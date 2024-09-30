# K8s Autosacling Demo

This project is a demo of Kubernetes Horizontal Pod Autoscaler (HPA) and a simple web application.

## Disclaimer

This demo was only tested on macOS.

## Prerequisites

- [Kind](https://kind.sigs.k8s.io/) installed 
- [kubectl](https://kubernetes.io/docs/reference/kubectl/) installed
- [ab](https://httpd.apache.org/docs/2.4/programs/ab.html) installed

## Setup

run `make setup` to create a cluster, deploy the application, setup autoscaling, run the proxy and forward the port to the webapp-service.

- after the setup finished, the dashboard opens automatically in the browser, wail approximately 10 seconds until proxy is ready.
- then reload the dashboard.
- the login token was automatically copied to the clipboard. (on macOS)

## Usage

run `make demo-full` to run a load test with 10 concurrent users.

run `make demo-partial` to run a load test with 3 concurrent users.
