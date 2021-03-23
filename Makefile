all: run

NETWORK ?= ophyd-tango_default

build:
	docker build -t ophyd-tango .

compose: show_network
	docker-compose up --build

run: build show_network
	docker run --network $(NETWORK) -it ophyd-tango

.PHONY: run build compose show_network
