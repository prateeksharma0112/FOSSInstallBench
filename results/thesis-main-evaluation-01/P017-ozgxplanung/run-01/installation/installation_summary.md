Built the xPlanBox (ozgxplanung) 9.4-SNAPSHOT from source in the /workspace Maven multi-module repository.

Prerequisites installed (absent initially): OpenJDK 17 (apt), Apache Maven 3.9.9 (downloaded to /opt/apache-maven-3.9.9, symlinked as /usr/local/bin/mvn), unzip. Ubuntu's packaged Maven 3.6.3 was bypassed because the POM enforces Maven >= 3.9.

Build method used (final): 
1) `mvn -B clean install -DskipTests` from /workspace → BUILD SUCCESS, 60/60 modules, 12:33 min.
2) `mvn -B install -P distribution -DskipTests` → BUILD SUCCESS, 5:56 min, producing the xplan-distribution assembly.

Tests were skipped because required runtime services (PostgreSQL/PostGIS, RabbitMQ, S3) are not available in the container; the README documents -DskipTests as the supported option in this situation.

Artifacts produced (absolute paths under /workspace):
- 14 WARs: xplan-manager/{xplan-manager-web,xplan-manager-api}/target, xplan-validator/{xplan-validator-web,xplan-validator-api}/target, xplan-webservices/xplan-webservices-services/{xplan-services-wfs,xplan-services-wfs-syn,xplan-services-wms}/target, xplan-webservices/xplan-webservices-validator-wms/target, xplan-webservices/xplan-webservices-inspireplu/target, xplan-dokumente/xplan-dokumente-api/target, xplan-documentation/xplan-webpages/target.
- /workspace/xplan-validator/xplan-validator-executor/target/xplan-validator-executor-9.4-SNAPSHOT.jar (Spring Boot executable).
- /workspace/xplan-cli/target/xplan-cli-9.4-SNAPSHOT.zip.
- Config/workspace ZIPs (manager-config-default, validator-config, dokumente-config, mapserver/mapproxy/ldproxy config, all deegree workspaces, database-scripts).
- /workspace/xplan-distribution/target/xplan-distribution-9.4-SNAPSHOT.zip (1.19 GB) holding web/, conf/, bin/, doc/, test/ — all components listed in the installation guide's overview table.

The runtime deployment described in the installation guide (three Tomcat instances, PostgreSQL/PostGIS, RabbitMQ quorum queues, S3 buckets, MapServer/MapProxy/ldproxy, HALE, Keycloak) was not performed because it depends on external infrastructure not provided in this environment; the source-build/installation deliverable was completed and verified.