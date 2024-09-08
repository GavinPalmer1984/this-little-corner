start-es-local:
	cd src/docker && make es

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
