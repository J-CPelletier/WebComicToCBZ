import requests, os
from lxml import html
from urllib.parse import urljoin
from zipfile import ZipFile
import click

class Comic:
    def __init__(self, start_url, next_page_selector, comic_image_selector):
        self.url = start_url
        self.next_page_selector = next_page_selector
        self.comic_image_selector = comic_image_selector
        self.current_page = 1

    def download(self, directory_name="finalComic"):
        """
        Downloads an entire Webcomic page by page starting from the first one
        and saves them in the directory_name created in the current working directory
        """
        os.makedirs(directory_name)
        while True:
            click.echo("Downloading page {}".format(self.url))
            response = requests.get(self.url)
            parsed_html = html.fromstring(response.content)

            image_element = parsed_html.xpath(self.comic_image_selector)
            next_link = parsed_html.xpath(self.next_page_selector)

            if image_element == []:
                click.echo("Could not find comic image.")
            else:
                try:
                    image_url = urljoin(self.url, image_element[0])
                    self.save_image(image_url, directory_name)
                except:
                    click.echo("The image couldn't be downloaded.")

            self.current_page += 1
            if next_link == [] or next_link[0].endswith("#"):
                break
            self.url = urljoin(self.url, next_link[0])
        click.echo("Finished downloading the images.")

    def save_image(self, image_url, directory_name):
        """
        Gets the image from the image_url and saves it in the directory_name
        """
        click.echo("Saving image {}".format(image_url))
        res = requests.get(image_url)
        res.raise_for_status()
        image_path = self.save_image_location(image_url, directory_name)
        if os.path.isfile(image_path):
            click.echo("The image was already downloaded. Skipping...")
        else:
            # Save the image
            with open(image_path, 'wb') as image_file:
                image_file.write(res.content)

    def save_image_location(self, url, directory):
        """
        Returns the location in the filesystem under which the webcomic will be saved
        """
        if url.count(".") <= 1:
            # No file extension (only dot in url is domain name)
            file_name = str(self.current_page)
        else:
            file_name = "{}{}".format(self.current_page, url[url.rindex("."):])
        return "/".join([directory, file_name])

    @staticmethod
    def make_cbz(comic_name, source_directory="finalComic"):
        """
        Takes all of the previously downloaded pages and compresses them in
        a .cbz file, erasing them afterwards.
        """
        cbz_file = ZipFile("{}.cbz".format(comic_name), mode="w")
        images = os.listdir("{}".format(source_directory))
        for image in images:
            image_location = "{}/{}".format(source_directory, image)
            cbz_file.write(image_location)
            os.remove(image_location)
        os.rmdir(source_directory)
        if cbz_file.testzip() != None:
            click.echo("Error while testing the archive; it might be corrupted.")
            cbz_file.close()
        else:
            cbz_file.close()
    @staticmethod
    def verify_xpath(url, next_page, image):
        """
        Takes a url and the XPath expressions for the next_page and image to go three pages
        into the comic. It returns a tuple containing the url of each page and their respective
        image urls.
        """
        verification = []
        for _ in range(3):
            response = requests.get(url)
            parsed_html = html.fromstring(response.content)

            image_element = parsed_html.xpath(image)[0]
            image_url = urljoin(url, image_element)
            next_link = parsed_html.xpath(next_page)[0]
            verification.append((url, image_url))
            url = urljoin(url, next_link)
        return verification