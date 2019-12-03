# Milestone3

- Task1/Task2/Task3

--

# If you want to ...

- **Test the overall workflow**

	- Test on Elastic Beanstalk at [http://seeb-env.twuqj3ymuy.us-east-1.elasticbeanstalk.com/](http://seeb-env.twuqj3ymuy.us-east-1.elasticbeanstalk.com/)
	- If you request the page which needs login first but you don't, it will jump to login page.
	- You can test:
		- Login/Registration
		- Search user profile
		- Update/Delete (Auth function)
		- Update concurrently (Etag)
		- ...

- **Modify the code**

	- When you run the code on your localhost, you should modify the request link in html file. Otherwise you will request my Elastic Beanstalk.
	- They are:
		- Two links in login_register.html
		- One link in homepage.html
		- One link in profile.html
