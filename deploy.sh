PROJECT_ID=$(gcloud config get-value project)
REPO="demo"
LOCATION="europe-west1"
IMAGE="assistant-mes-droits"
SERVICE_NAME="assistant-mes-droits"
VERSION="latest"
GAR_TAG=$LOCATION-docker.pkg.dev/$PROJECT_ID/$REPO/$IMAGE:$VERSION

# Create repository
gcloud artifacts repositories create $REPO --repository-format=docker \
    --location=$LOCATION --description="Docker repository" \
    --project=$PROJECT_ID  || true # If fails because already exist then its fine

# Build image
gcloud builds submit --tag $GAR_TAG

# Deploy Cloud run
gcloud run deploy $SERVICE_NAME --image=$GAR_TAG --max-instances=1 --min-instances=1 --port=8080 \
	--allow-unauthenticated --region=europe-west1 --memory=0.5Gi --cpu=1 -q --session-affinity \
	--service-account=cloud-run@$PROJECT_ID.iam.gserviceaccount.com --concurrency 300 --timeout 300 \
	$(awk '!/^#/ && NF {printf "--set-env-vars %s ", $0}' .env) --cpu-throttling
