# GraphHopper Routing Engine

## Get Started

To get started you can try [GraphHopper Maps](README.md#graphhopper-maps), read through [our documentation](./docs/index.md) and install GraphHopper including the Maps UI locally.

* 11.x: [documentation](https://github.com/graphhopper/graphhopper/blob/11.x/docs/index.md)
  , [web service jar](https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/11.0/graphhopper-web-11.0.jar)
  , [announcement](https://www.graphhopper.com/blog/2025/10/14/graphhopper-routing-engine-11-0-released/)
* unstable master: [documentation](https://github.com/graphhopper/graphhopper/blob/master/docs/index.md)

See the [changelog file](./CHANGELOG.md) for Java API Changes.

## Installation

To install the [GraphHopper Maps](https://graphhopper.com/maps/) UI and the web service locally you [need a JVM](https://adoptium.net) (>= Java 25) and do:

```bash
wget https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/11.0/graphhopper-web-11.0.jar \
  https://raw.githubusercontent.com/graphhopper/graphhopper/11.x/config-example.yml \
  http://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf
java -D"dw.graphhopper.datareader.file=berlin-latest.osm.pbf" -jar graphhopper*.jar server config-example.yml
```

After a while you see a log message with 'Server - Started', then go to http://localhost:8989/ and
you'll see a map of Berlin. You should be able to right click on the map to create a route.

See the [documentation](./docs/index.md) that contains e.g. [the elevation guide](./docs/core/elevation.md) and the [deployment guide](./docs/core/deploy.md).

### Docker

The Docker images created by the community from the `master` branch can be found [here](https://hub.docker.com/r/israelhikingmap/graphhopper)
(currently daily). See the [Dockerfile](https://github.com/IsraelHikingMap/graphhopper-docker-image-push) for more details.
