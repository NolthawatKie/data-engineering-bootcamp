import csv

import json
import os

import scrapy
from scrapy.crawler import CrawlerProcess

# Import pacakge to upload file to GCS
from google.cloud import storage
from google.oauth2 import service_account


URL = "https://ทองคําราคา.com/"
dt = "2023-04-24"


class MySpider(scrapy.Spider):
    name = "gold_price_spider"
    start_urls = [URL,]

    def parse(self, response):
        header = response.css("#divDaily h3::text").get().strip()
        print(header)

        table = response.css("#divDaily .pdtable")
        # print(table)

        rows = table.css("tr")
        # rows = table.xpath("//tr")
        # print(rows)

        for row in rows:
            print(row.css("td::text").extract())
            # print(row.xpath("td//text()").extract())

        # Write to CSV
        # YOUR CODE HERE

        # Write to csv file
        with open("gold_prices.csv", "w") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row.css("td::text").extract())

        # upload to DataLake

        # keyfile = os.environ.get("KEYFILE_PATH")
        keyfile = "dataengineercafe-446d449e814b-gcs.json"
        service_account_info = json.load(open(keyfile))
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info)
        project_id = "dataengineercafe"

        storage_client = storage.Client(
            project=project_id,
            credentials=credentials,
        )
        bucket = storage_client.bucket("kan-100001")

        blob = bucket.blob(f"{dt}/gold_prices.csv")
        blob.upload_from_filename("gold_prices.csv")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
