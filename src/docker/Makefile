elastic:
	docker pull docker.elastic.co/elasticsearch/elasticsearch:8.3.2
	docker network create elastic || true
	-- docker rm es01
	docker run --name es01 --net elastic -p 9200:9200 -p 9300:9300 -e xpack.security.enabled=true -e xpack.security.http.ssl.enabled=false -e discovery.type=single-node -it docker.elastic.co/elasticsearch/elasticsearch:8.3.2

cert:
	docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .

setup-password:
	docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive
