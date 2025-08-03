GCP_PROJECT=db-final-project-9e32f
GCP_SERVICE=db-final-project
GCP_REGION=asia-northeast1

deploy:
	gcloud run deploy ${GCP_SERVICE} \
		--project ${GCP_PROJECT} \
		--region ${GCP_REGION} \
		--allow-unauthenticated \
		--source .
