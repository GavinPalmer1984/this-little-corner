start-es-local:
	cd src/docker && make elastic

copy-es-cert:
	cd src/docker && make cert

setup-python:
	python3.11 -m venv venv
	source venv/bin/activate

setup-coth:
	python src/utils/scrape_youtube_channel.py https://www.youtube.com/@churchofthehighlandsAL
	python src/utils/scraper.py

setup-acc:
	python src/utils/scrape_youtube_channel.py https://www.youtube.com/@auburncommunitychurch
	python src/utils/scraper.py

index:
	python src/utils/scraper.py

build-client:
	cd src/search-app/SearchClient && rm -rf dist
	cd src/search-app/SearchClient && yarn
	cd src/search-app/SearchClient && NODE_OPTIONS=--openssl-legacy-provider yarn prod

build-server:
	cd src/search-app/SearchServer && dotnet restore ./SearchServer.csproj
	cd src/search-app/SearchServer && dotnet build ./SearchServer.csproj --configuration=Release

build-artifacts:
	cd src/search-app && rm -rf out
	cd src/search-app && mkdir -p out/dist

	cd src/search-app && cp -r SearchClient/dist/* out/dist/
	cd src/search-app && cp -r SearchClient/public/* out/dist/
	cd src/search-app && cp -r SearchServer/bin/Release/net6.0/* out/

build: build-client build-server build-artifacts

start:
	./src/search-app/out/SearchServer
