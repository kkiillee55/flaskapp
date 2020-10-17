This branch inherits all codes form main branch, the goal is to make the website look more beautiful!
Initially, I just want to find a html resume template, but later I finf more bootstrap templates, so I decide to give this website a brand new look

I only know a little bit about css and js, but it seems okay, all I need to do is to put those css and js files in a proper directory and import them in html files,
and modify contents in old templates to fit new styles.

After finisheing the styling stuffs, I then changed the database to Postgresql, and run the website and postgresql locally to verify they did acutally work.

Then I tried to build the docker image of this web application locally. I write a simple docker file and run docker build, it gives me an error, which say the pg_config is not found, the reason is that postgresql is not installed in docker vm, so I need to add more RUN commands to install postgre and then run pip install

Finally, I put every in AWS. I first create a Postgre db in RDS, and test the connection. Then I started an EC2 instance, git clone this branch, create docker image of this web
application and push it to ECR, finally, I create a cluster in ECS and run the conatiner image uploaded just now in AWS. and here's a screenshot:

<img src="https://github.com/kkiillee55/flaskapp/blob/add-resume/successful.PNG">




