# Makefile for managing the project

# Build all containers
build-all:
	docker-compose build

# Start all containers in detached mode
up-all:
	docker-compose up -d

# Build and start Lightdash
init-lightdash:
	brew install minikube && \
	minikube start --memory=4096 && \
	helm repo add lightdash https://lightdash.github.io/helm-charts && \
	kubectl create namespace lightdash && \
	helm install lightdash lightdash/lightdash -n lightdash -f k8s/lightdash/values.yaml && \
	

# Stop all containers
down-all:
	docker-compose down

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




.PHONY: build-all up-all init-lightdash down-all stop-minikube delete-minikube
