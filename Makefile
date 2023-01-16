build:
	docker build -t jester-bot .
	heroku container:push jester-bot -a jester-bot-2
deploy:
	heroku container:release jester-bot -a jester-bot-2
downscale:
	heroku ps:scale --app=jester-bot-2 jester-bot=0 
upscale:
	heroku ps:scale --app=jester-bot-2 jester-bot=1 
