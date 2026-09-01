# Installation & Local Development

You can use Edalicits as a SAS service at https://www.edalitics.com/. 

Or you can deploy a local instance of edalitics in your environment.  To do this you should: 

## Clone the repository

```bash
git clone github.com/jortilles/EDA.git
```

## Configure the database

Edit the MongoDB connection in:  **EDA/eda/eda_api/config/database.config.js**

```
module.exports = {
    url: "mongodb://127.0.0.1:27017/EDA"
};
```

## Configure the backend URL in the UI

In: **EDA/eda/eda_app/src/app/config/config.ts**
```
export const URL_SERVICES = 'http://localhost:8666';
```

## Run the backend and frontend
Backend API:
```bash
cd EDA/eda/eda_api
npm install
npm start
```
Frontend App
```bash
cd EDA/eda/eda_app
npm install
npm start
```

The application will be available in your browser at:

👉 http://localhost:4200



## 🐳 Run edalitics with Docker (recommended)

This is the siplest way to run edalitics locally 
To get the latests buld: 
```bash
docker run -p 80:80 jortilles/eda:latest
```
To get a manual deploy: 
```bash
docker run -p 80:80 jortilles/eda:manual_latest
```

Then open:

👉 http://localhost



Default credentials:

**User:** eda@jortilles.com

**Password:** default
