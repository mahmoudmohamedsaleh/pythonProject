#!/usr/bin/env bash
# ============================================================
# EJTech CRM — Full GCP Cloud Run Deployment Script
#
# Prerequisites (do these ONCE before running):
#   1. Create a Google Cloud account at https://cloud.google.com
#   2. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
#      OR run this entirely in GCP Cloud Shell (no install needed)
#   3. Have Docker installed locally (skip if using Cloud Build)
#   4. Have your ejtech_crm.dump file ready (run db_export.sh first)
#
# Usage:
#   Edit the VARIABLES section below, then:
#   bash deploy_gcp.sh
# ============================================================

set -e

# ============================================================
# VARIABLES — Edit these before running
# ============================================================
PROJECT_ID="ejtech-crm"                      # Your GCP project ID (must be globally unique)
REGION="me-central1"                          # GCP region (me-central1 = Middle East/Doha)
                                              # Other options: europe-west1, us-central1, asia-east1
SERVICE_NAME="ejtech-crm"                    # Cloud Run service name
REPO_NAME="ejtech-repo"                      # Artifact Registry repository name
DB_INSTANCE="ejtech-db"                      # Cloud SQL instance name
DB_NAME="ejtech"                             # PostgreSQL database name
DB_USER="ejtech"                             # PostgreSQL user
DB_PASSWORD="CHANGE_ME_STRONG_PASSWORD"      # PostgreSQL password — CHANGE THIS
DUMP_FILE="ejtech_crm.dump"                  # Path to your database dump file

# Secrets (values from your Replit Secrets panel)
SECRET_KEY_VALUE="CHANGE_ME_FLASK_SECRET_KEY"
OPENAI_API_KEY_VALUE="sk-..."
RESEND_API_KEY_VALUE="re_..."

# ============================================================
# STEP 1 — Authenticate and set project
# ============================================================
echo ""
echo "=========================================="
echo " STEP 1: Authenticate with Google Cloud"
echo "=========================================="
gcloud auth login
gcloud config set project "$PROJECT_ID" || {
    echo "Project not found. Creating project $PROJECT_ID..."
    gcloud projects create "$PROJECT_ID" --name="EJTech CRM"
    gcloud config set project "$PROJECT_ID"
}

echo "Linking billing account..."
echo "  >> Open https://console.cloud.google.com/billing and link billing to project $PROJECT_ID"
echo "  >> Then press ENTER to continue."
read -r

# ============================================================
# STEP 2 — Enable required GCP APIs
# ============================================================
echo ""
echo "=========================================="
echo " STEP 2: Enable GCP APIs"
echo "=========================================="
gcloud services enable \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

echo "APIs enabled."

# ============================================================
# STEP 3 — Create Artifact Registry repository
# ============================================================
echo ""
echo "=========================================="
echo " STEP 3: Create Artifact Registry repo"
echo "=========================================="
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="EJTech CRM Docker images" \
    --project="$PROJECT_ID" 2>/dev/null || echo "  (repository already exists, skipping)"

# ============================================================
# STEP 4 — Build and push Docker image
# ============================================================
echo ""
echo "=========================================="
echo " STEP 4: Build and push Docker image"
echo "=========================================="
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "Building image: $IMAGE"
docker build -t "$IMAGE" .

echo "Pushing image..."
docker push "$IMAGE"

echo "Image pushed: $IMAGE"

# ============================================================
# STEP 5 — Create Cloud SQL PostgreSQL instance
# ============================================================
echo ""
echo "=========================================="
echo " STEP 5: Create Cloud SQL instance"
echo "  (this takes 5-10 minutes)"
echo "=========================================="
gcloud sql instances create "$DB_INSTANCE" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --storage-type=SSD \
    --storage-size=20GB \
    --backup-start-time="02:00" \
    --availability-type=zonal 2>/dev/null || echo "  (instance already exists, skipping)"

echo "Setting database password..."
gcloud sql users set-password postgres \
    --instance="$DB_INSTANCE" \
    --password="$DB_PASSWORD" \
    --project="$PROJECT_ID" 2>/dev/null || true

echo "Creating database and user..."
gcloud sql databases create "$DB_NAME" \
    --instance="$DB_INSTANCE" \
    --project="$PROJECT_ID" 2>/dev/null || echo "  (database already exists, skipping)"

gcloud sql users create "$DB_USER" \
    --instance="$DB_INSTANCE" \
    --password="$DB_PASSWORD" \
    --project="$PROJECT_ID" 2>/dev/null || echo "  (user already exists, skipping)"

# ============================================================
# STEP 6 — Import database dump into Cloud SQL
# ============================================================
echo ""
echo "=========================================="
echo " STEP 6: Import database dump"
echo "=========================================="

if [ ! -f "$DUMP_FILE" ]; then
    echo "  WARNING: $DUMP_FILE not found. Skipping import."
    echo "  Run db_export.sh on Replit first, then copy the dump file here."
else
    # Get Cloud SQL Public IP
    CLOUD_SQL_IP=$(gcloud sql instances describe "$DB_INSTANCE" \
        --project="$PROJECT_ID" \
        --format="value(ipAddresses[0].ipAddress)")

    echo "Cloud SQL Public IP: $CLOUD_SQL_IP"
    echo "Authorizing your current IP for Cloud SQL access..."
    MY_IP=$(curl -s https://api.ipify.org)
    gcloud sql instances patch "$DB_INSTANCE" \
        --authorized-networks="$MY_IP/32" \
        --project="$PROJECT_ID" --quiet

    echo "Restoring dump (this may take several minutes)..."
    PGPASSWORD="$DB_PASSWORD" pg_restore \
        --no-owner \
        --no-acl \
        -h "$CLOUD_SQL_IP" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        "$DUMP_FILE" || echo "  (some errors during restore are normal for pg_restore)"

    echo "Installing custom PostgreSQL functions..."
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$CLOUD_SQL_IP" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -f cloud_sql_functions.sql

    echo "Database import complete."
fi

# ============================================================
# STEP 7 — Store secrets in GCP Secret Manager
# ============================================================
echo ""
echo "=========================================="
echo " STEP 7: Store secrets in Secret Manager"
echo "=========================================="

CLOUD_SQL_CONNECTION="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
DATABASE_URL_VALUE="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CLOUD_SQL_CONNECTION}"

store_secret() {
    local name="$1"
    local value="$2"
    echo -n "$value" | gcloud secrets create "$name" \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || \
    echo -n "$value" | gcloud secrets versions add "$name" \
        --data-file=- \
        --project="$PROJECT_ID"
    echo "  Stored secret: $name"
}

store_secret "EJTECH_DATABASE_URL"  "$DATABASE_URL_VALUE"
store_secret "EJTECH_SECRET_KEY"    "$SECRET_KEY_VALUE"
store_secret "EJTECH_OPENAI_KEY"    "$OPENAI_API_KEY_VALUE"
store_secret "EJTECH_RESEND_KEY"    "$RESEND_API_KEY_VALUE"

# Grant Cloud Run service account access to secrets
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET in EJTECH_DATABASE_URL EJTECH_SECRET_KEY EJTECH_OPENAI_KEY EJTECH_RESEND_KEY; do
    gcloud secrets add-iam-policy-binding "$SECRET" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID" --quiet
done

echo "Secrets stored and permissions granted."

# ============================================================
# STEP 8 — Grant Cloud Run access to Cloud SQL
# ============================================================
echo ""
echo "=========================================="
echo " STEP 8: Grant Cloud Run → Cloud SQL access"
echo "=========================================="
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/cloudsql.client" \
    --quiet

echo "Cloud SQL client role granted."

# ============================================================
# STEP 9 — Deploy to Cloud Run
# ============================================================
echo ""
echo "=========================================="
echo " STEP 9: Deploy to Cloud Run"
echo "=========================================="
CLOUD_SQL_CONNECTION="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=10 \
    --timeout=300 \
    --concurrency=80 \
    --add-cloudsql-instances="$CLOUD_SQL_CONNECTION" \
    --set-secrets="DATABASE_URL=EJTECH_DATABASE_URL:latest,SECRET_KEY=EJTECH_SECRET_KEY:latest,OPENAI_API_KEY=EJTECH_OPENAI_KEY:latest,RESEND_API_KEY=EJTECH_RESEND_KEY:latest" \
    --set-env-vars="FLASK_ENV=production" \
    --project="$PROJECT_ID"

# ============================================================
# STEP 10 — Print service URL
# ============================================================
echo ""
echo "=========================================="
echo " DEPLOYMENT COMPLETE"
echo "=========================================="
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

echo ""
echo "  Your app is live at: $SERVICE_URL"
echo ""
echo "  Cloud SQL connection: $CLOUD_SQL_CONNECTION"
echo "  Docker image:         $IMAGE"
echo ""
echo "  To view logs:"
echo "    gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "  To update the app after code changes:"
echo "    docker build -t $IMAGE . && docker push $IMAGE"
echo "    gcloud run deploy $SERVICE_NAME --image $IMAGE --region $REGION --project $PROJECT_ID"
echo ""
