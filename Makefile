# Install dependencies
deps:
	brew install minikube && \
	brew install lazydocker

# Build all containers
build:
	docker-compose build

# Start all containers in detached mode
up:
	docker-compose up -d --remove-orphans

rebuild:
	make build && make up

duckdb-bash:
	docker-compose exec duckdb bash

pyscript-bash:
	docker-compose exec pyscript bash

# Build and start Lightdash
init-lightdash:
	brew install minikube && \
	minikube start  && \
	helm repo add lightdash https://lightdash.github.io/helm-charts && \
	kubectl create namespace lightdash && \
	helm install lightdash lightdash/lightdash -n lightdash -f k8s/lightdash/values.yaml
	
# Stop all containers
down-all:
	docker-compose down

destroy-docker:
	docker-compose down -v

# Stop Minikube
stop-minikube:
	minikube stop

# Destroy Minikube cluster
destroy-minikube:
	minikube delete --all --purge

destroy-lightdash:
	helm uninstall lightdash -n lightdash
	minikube delete --all --purge

rebuild-lightdash:
	minikube start --memory=4096 --cpus=2 --driver=docker
	helm install lightdash lightdash/lightdash -n lightdash -f values.yaml

show-lightdash: 
	kubectl get svc -n lightdash && \
	echo " " && \
	kubectl get pods -n lightdash

postgres-shell:
	docker-compose exec postgres psql -U postgres -d mydatabase

duckdb-query:
	docker-compose exec duckdb python3 -m olap


.PHONY: build-all up-all init-lightdash down-all stop-minikube delete-minikube
