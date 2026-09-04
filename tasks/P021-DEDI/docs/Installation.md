# Local Setup

To run the **DEUTSCHLAND.DIGITAL** locally, you need:

## Prerequisites

Install the following:
- JDK-17
- Postgres
- Docker
- IDE for Java (eg. IntelliJ)


## Clone projects
  - `User Service`: https://gitlab.opencode.de/DEUTSCHLAND.DIGITAL/plattform/service/user-service 
  - `Media Service`: https://gitlab.opencode.de/DEUTSCHLAND.DIGITAL/plattform/service/media-service    
  - `Keycloak Service`:https://gitlab.opencode.de/DEUTSCHLAND.DIGITAL/plattform/service/DeDi-keycloak
  - `Geo Service`: https://gitlab.opencode.de/DEUTSCHLAND.DIGITAL/plattform/service/geo-service
  - `Key Management service`: https://gitlab.opencode.de/DEUTSCHLAND.DIGITAL/plattform/service/key-management-service

## Start the services

### Docker
  - Adjust the [docker-compose.yml](./docker-compose.yml). This will start dependencies that are required by almost all services:

    - postgres
    - keycloak
    - mailhog
    - zookeeper
    - kafka

  - Start the containers:

 ```shell
docker-compose up -d
```

### Services

  - adjust the configuration properties in the `application.yml`
  - run 
```shell
mvn clean install
```

Please refer to each service for details on how to start them.


## Generate NPM Packages

Once the services are running, you need to download the json file under `<service-url>/v3/api-docs/` file and generate the corresponding Typescript SDK using [openapi-generator](https://github.com/OpenAPITools/openapi-generator). 


Follow the steps in [Generate SDK and NPM registry](./GeneratePackages.md) for each service and also for the `shared-library`. 


Replace references to the SLR packages in the `package.json` with the your newly created packages:

current:

  - `@SLR/shared-library`
  - `@SLR/user-service-external-sdk`
  - `@SLR/media-service-sdk` 
  - `@SLR/key-management-service-sdk`  
  - `@SLR/geo-service-sdk`  
new:

  - `@<your-group>/shared-library`
  - `@<your-group>/user-service-external-sdk`
  - `@<your-group>/media-service-sdk` 
  - `@<your-group>/key-management-service-sdk`  
  - `@<your-group>/geo-service-sdk`  