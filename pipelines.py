# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import os
#import sqlite3

class ScrapingInfoPipeline(object):
	
	def __init__(self):
		self.create_connection()
		self.create_table()
		
	def create_connection(self):
		DATABASE_URL = os.environ['DATABASE_URL']
		self.connect = psycopg2.connect(DATABASE_URL, sslmode='require')
		self.cursor = self.connect.cursor()
		'''
		self.connect = sqlite3.connect('afisha_infos.db')
		self.cursor = self.connect.cursor()
		'''
	def create_table(self):
		#self.cursor.execute(''' DROP TABLE IF EXISTS afisha_infos ''')
		self.cursor.execute(''' CREATE TABLE IF NOT EXISTS afisha_infos
							(ID SERIAL PRIMARY KEY,
							TITLE TEXT NOT NULL,
							DESCRIPTION TEXT NOT NULL,
							LOCATION TEXT NOT NULL,
							URL TEXT NOT NULL); ''')
	
	def process_item(self, item, spider):
		self.store_db(item)
		self.connect.commit()
		return item
		
	def store_db(self, item):
		self.cursor.execute(
				"INSERT INTO afisha_infos (title, description, location, url) VALUES (%s, %s, %s, %s)", 
				(item['title'], item['description'], item['location'], item['url']))
				
		self.connect.commit()

'''
	def open_spider(self, spider):
		
		DATABASE_URL = os.environ['DATABASE_URL']
		self.connect = psycopg2.connect(DATABASE_URL, sslmode='require')
		
		
		self.cursor = self.connect.cursor()
		print("Database opened successfully")
		
		self.cursor = self.connect.cursor()
		
	def close_spider(self, spider):
		self.cursor.close()
		self.connect.close()
'''
