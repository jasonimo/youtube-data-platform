region            = "us-east-1"
project_name      = "youtube-job"
ecr_repository_name = "youtube-job"

# Use the same tag you pushed to ECR (git SHA)
image_tag         = "11e6fdc990c0698fe803eb05408918a47a34064d"

youtube_api_key   = "AIzaSyAwgdDBVhAGIuriGEsORSxwj5Pp7oLH7Lo"

# daily schedule (change later)
schedule_expression = "rate(1 day)"