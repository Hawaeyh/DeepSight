# Firebase deployment

DeepSight has two deployable parts:

- `frontend/`: static Vite application hosted by Firebase Hosting.
- `backend/`: FastAPI and PyTorch service hosted by Google Cloud Run.

Firebase Hosting alone cannot execute the Python backend. The frontend must be built with the public Cloud Run API URL.

## Prerequisites

1. Create a Firebase project and a Firestore database in production mode.
2. Enable Cloud Run, Cloud Build, and Artifact Registry in the linked Google Cloud project.
3. Install and authenticate the CLIs:

```powershell
npm install -g firebase-tools
firebase login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Cloud Run deployment requires billing to be enabled on the project.

## Deploy the backend

Create these secrets in Google Cloud Secret Manager before deployment:

- `deepsight-secret-key`: a long random JWT signing key.
- `deepsight-database-url`: the production SQLAlchemy database URL.
- `deepsight-google-client-id`: the Google OAuth web client ID.

Copy `backend/env.cloudrun.example.yaml` to `backend/env.cloudrun.yaml` and replace the Firebase project ID. The copied file is local deployment configuration and should not contain secrets.

From the repository root:

```powershell
gcloud run deploy deepsight-api `
  --source backend `
  --region asia-southeast1 `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --timeout 900 `
  --env-vars-file backend/env.cloudrun.yaml `
  --set-secrets "SECRET_KEY=deepsight-secret-key:latest,DATABASE_URL=deepsight-database-url:latest,GOOGLE_CLIENT_ID=deepsight-google-client-id:latest"
```

Cloud Run supplies Application Default Credentials to the Firebase Admin SDK, so a service-account JSON file should not be placed in the container. Grant the Cloud Run service account access to Firestore and permission to read the three secrets.

After deployment, note the service URL, for example:

```text
https://deepsight-api-xxxxx-as.a.run.app
```

Test the backend:

```powershell
Invoke-WebRequest https://YOUR_CLOUD_RUN_URL/api/v1/health
```

## Configure the frontend

Create `frontend/.env.production` locally:

```env
VITE_API_URL=https://YOUR_CLOUD_RUN_URL/api/v1
VITE_GOOGLE_CLIENT_ID=YOUR_WEB_CLIENT_ID.apps.googleusercontent.com
```

Add both Firebase domains to the OAuth web client's authorized JavaScript origins:

```text
https://YOUR_PROJECT_ID.web.app
https://YOUR_PROJECT_ID.firebaseapp.com
```

Also include both domains in the backend `FRONTEND_ORIGINS` value.

## Deploy Firebase Hosting

Copy `.firebaserc.example` to `.firebaserc` and replace the project ID, or select it with the CLI:

```powershell
firebase use --add
npm --prefix frontend run build
firebase deploy --only hosting
```

The React single-page application rewrite is already configured in `firebase.json`.

## Important production storage note

The current application uses SQLAlchemy as its primary store and mirrors analyses and feedback to Firestore. SQLite files are ephemeral and unsafe for multiple Cloud Run instances. Before production, set `DATABASE_URL` to a managed database such as Cloud SQL PostgreSQL, or complete a migration that makes Firestore the primary store for users, subscriptions, usage, analyses, and feedback.

For PostgreSQL, use a SQLAlchemy URL beginning with `postgresql+psycopg://`. When using Cloud SQL, also attach the Cloud SQL instance to the Cloud Run service and grant the service account the Cloud SQL Client role.

Uploaded media and generated reports are also local files today. Cloud Run local storage is ephemeral; move these files to Cloud Storage before treating the deployment as durable production hosting.
