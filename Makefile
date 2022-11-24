# import .env
cnf ?= .env
include $(cnf)
export $(shell sed 's/=.*//' $(cnf))

APP_NAME = lgu_plus_async_api
MODEL_VOLUME = /home/sch9027/workspace/lgu_plus_async:/app

# # Build and run the container
# build:
# 	@echo 'build docker $(APP_NAME)'
# 	docker build --no-cache -t $(APP_NAME) . 

# run:
# 	@echo 'run docker $(APP_NAME)'
# 	docker run -d -t --name="$(APP_NAME)" --net=host --ipc=host --shm-size 32gb -v $(MODEL_VOLUME) --cpuset-cpus="32-47" --gpus all $(APP_NAME)

# stop:
# 	@echo 'stop docker $(APP_NAME)'
# 	docker stop $(APP_NAME)

rm-api:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f $(APP_NAME)
rm-redis:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f lgu_plus_async_redis
rm-rabbitmq:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f lgu_plus_async_rabbitmq
rm-worker:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f lgu_plus_async_worker

# rmi:
# 	@echo 'rmi docker $(APP_NAME)'
# 	docker rmi $(APP_NAME)
	
# Build and run the container
up: ## Spin up the project
	@echo 'docker-compose up LGU_PLUS_ASYNC v2.0'
	docker compose -f docker-compose.yml up -d --build