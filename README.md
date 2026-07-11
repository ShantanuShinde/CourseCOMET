# CourseCOMET

## Loading database into PostgreSQL

With PostgreSQL installed in your machine, run the following command to load `dump.backup` into your Postgres server.
>  pg_restore -v --no-owner --no-acl -d "\<your-postgres-database-connection-string>" dump.backup

## Running the Chatbot Server
1. Go to the back_end directory.
2. Install the required libraries using:
> pip install -r requirements.txt
3. Create a `.env` file in the directory and add following 2 variables:
    1. OPENAI_API_KEY=\<your-openai-key>
    2. POSTGRES_PASSWORD=\<your-postgres-password>
4. Start the backend server using the following command:
>  uvicorn chatbot_api_server:app --reload

## Running the frontend server
1. Go to the front_end directory
2. Make sure you have nodejs installed.
3. Install nextjs and react using:
> npm install next react react-dom
3. Create a `.env` file in the directory and add following variable:
    1. BACKEND_URL=\<back-url-created-by-backend-server>/api/ask
4. Run the nodejs server using:
> npm run dev
5. The frontend should open up at the mentioned link in the output.

[Demo Video](https://www.youtube.com/watch?v=E-0W8S8kJyA&t=5s)

Checkout the [deployed website](https://course-comet.vercel.app/) with current changes

The project hosts the database on **Neon** to be used by the deployment. 
The backend is deployed to **Render** as a web service. 
The frontend is deployed to **Vercel**.