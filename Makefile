run:
    docker run --env-file=/root.env volumes3:v1

stop:
    docker stop volumes3

build
	 docker build -t volumes3 .

