# Instagram scraper

## Overview
This tool enables its users to extract public data from Instagram profiles and calculate, through a strictly defined procedure, metrics that are linked to the performance of both profiles (content creators) and posts.

The present tool is a key part of my dissertation with the title of *"From digital footprints to facts: mining social data for marketing practices"*, through which conclusions are drawn for the Greek Instagram community in three areas: 

- The behavior and preferences of the Greek Instagram & YouTube community 
- The tactics with which businesses operate on Instagram and YouTube
- The impact of COVID-19 virus on digital behavior of the users

## Useful Tools
- Python 3.6+
- Scrapy framework
- Web browser (recommended: Chrome or Mozilla browser)
- MongoDB

## Description
### Setting up our Scrapy spider
1. To install Scrapy simply enter the command *"pip install scrapy"* in the command line
2. Navigate to your project folder Scrapy automatically creates and run the “startproject” command along with the project name (“instascraper” in this case) and Scrapy will build a web scraping project folder for you, with everything already set up. So enter the commands in the order shown below:  
   * *scrapy startproject instascraper*
   * *cd instascraper*
   * *scrapy genspider instagram instagram.com*
### Structure of project folder
Once we have entered the above commands, Scrapy spider templates are set up. It should be noted that in this case we have two additional files:
- the *"resources"* folder
 <div dir='rtl'> created to store files that contain important data for the scraping mechanism, such as names of Instagram profiles. <\dir='rtl'>
- the *"tools"* folder
  created to store files that contain important data for the scraping mechanism, such as names of Instagram profiles.
