# docker buildx build --platform linux/amd64,linux/arm64 -t gcr.io/black-agility-429617-d3/demotool --push .

docker build --platform linux/amd64 -t gcr.io/black-agility-429617-d3/demotool .

docker push gcr.io/black-agility-429617-d3/demotool

gcloud run deploy qodia-demotool --image gcr.io/black-agility-429617-d3/demotool --platform managed --region europe-west3 --allow-unauthenticated