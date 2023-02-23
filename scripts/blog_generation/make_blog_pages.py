import random
from math import ceil
from os import walk
import os
from json import decoder

from jinja2 import Template


BLOG_PAGE_BASE_NAME = "blog_page_"


def read_all(filename, encoding=None):
    contents = ""
    with open(filename, mode='r', encoding=encoding) as f:
        while 1:
            line = f.readline()
            if not line:
                break
            contents += line

    return contents


class Pager:
    def __init__(self, link):
        self._link = link

        # Load post preview template
        self._pager_template = read_all("pager_template.html")

    def generate_forward(self):

        # Fill out parameters for jinja
        template_parameters = {
            "class": "next",
            "page_href": self._link,
            "button_text": "Next Page &rarr;"
        }

        # Run jinja
        j2_template = Template(self._pager_template)
        html = j2_template.render(template_parameters)

        return html

    def generate_backward(self):
        # Fill out parameters for jinja
        template_parameters = {
            "class": "previous",
            "page_href": self._link,
            "button_text": "&larr; Previous Page"
        }

        # Run jinja
        j2_template = Template(self._pager_template)
        html = j2_template.render(template_parameters)

        return html


class BlogPostPreview:
    def __init__(self, post_page_href, title, subtitle, post_date, background_image):
        self._post_page_href = post_page_href
        self._title = title
        self._subtitle = subtitle
        self._post_date = post_date
        self._background_image = background_image

        # Load post preview template
        self._blog_preview_template = read_all("post_preview_template.html")

    def get_background(self):
        return self._background_image

    def generate(self):

        # Fill out parameters for jinja
        post_preview_template_parameters = {
            "post_page_ref": self._post_page_href,
            "title": self._title,
            "subtitle": self._subtitle,
            "post_date": self._post_date,
        }

        # Run jinja
        j2_template = Template(self._blog_preview_template)
        html = j2_template.render(post_preview_template_parameters)

        return html


class BlogPagesGenerator:
    def __init__(self, num_previews_per_page=3):
        self._num_previews_per_page = num_previews_per_page

    def parse_post(self, json):
        # init parser
        return decoder.JSONDecoder().decode(json)

    def make_page_name(self, index):
        return BLOG_PAGE_BASE_NAME + str(index) + ".html"

    def generate_pages(self):

        # Load blog page template
        blog_page_template = read_all("blog_page_template.html")

        # Query for the blogs
        directories = dict()
        for (dirpath, dirnames, filenames_) in walk("../../blogs/"):
            filenames_clean = []
            for name in filenames_:
                if ".json" in name:
                    filenames_clean.append(name)

            # Save off all the file names under their directory
            directories[dirpath.split("/")[-1]] = filenames_clean

        # Process each directory - create a post struct for each
        preview_blocks = []
        for directory in directories.keys():

            # Parse each file in this directory
            for file in directories[directory]:

                # Load this file from disk
                file_path = os.path.join("..", os.path.join("..", os.path.join("blogs", os.path.join(directory, file))))
                blog_post_json = read_all(file_path)

                # Parse for required data - search for div with needed data
                data = self.parse_post(blog_post_json)

                # Create a preview class, add to list
                post_preview = BlogPostPreview(
                    data["post_page_href"],
                    data["title"],
                    data["sub_title"],
                    data["post_date"],
                    data["background_imag_name"]
                )
                preview_blocks.append(post_preview)

        # Calculate the number of pages
        total_num_pages = ceil(len(preview_blocks) / self._num_previews_per_page)

        # Iterate and create each page
        for page_index in range(0, total_num_pages):

            # Create the preview block body text
            preview_block_html = ""
            random_background = ""
            base_post_index = page_index * self._num_previews_per_page
            random_index = random.randrange(0, len(preview_blocks) - base_post_index - 1)
            for post_index in range(base_post_index, base_post_index + self._num_previews_per_page):
                # Generate this preview to text
                preview_html = preview_blocks[post_index].generate()

                # Add to body text for preview block
                preview_block_html += preview_html + "\n"

                # Grab the random index image
                if random_index == post_index:
                    random_background = preview_blocks[post_index].get_background()

            # Now add the correct buttons to the bottom
            if page_index == 0:
                if total_num_pages > 1:
                    # Generate a forward pager
                    pager = Pager(self.make_page_name(page_index+1))
                    preview_block_html += pager.generate_forward()
            else:
                # Pages with forward and back arrow (possibly)
                if page_index + 1 >= total_num_pages:
                    # Only a single arrow (backward)
                    pager = Pager(self.make_page_name(page_index-1))
                    preview_block_html += pager.generate_backward()
                else:
                    # Generate backward
                    pager = Pager(self.make_page_name(page_index-1))
                    preview_block_html += pager.generate_backward()

                    # Generate forward
                    pager = Pager(self.make_page_name(page_index+1))
                    preview_block_html += pager.generate_forward()

            # Fill out template parameters using jinja
            title = "Blog Page " + str(page_index)
            sub_title = ""  # TODO
            template_parameters = {
                "meta_description": "A blog page",
                "head_title": title,
                "background_image_name": random_background,
                "title": title.capitalize(),
                "sub_title": sub_title,
                "posts_block": preview_block_html,
            }

            # Run jinja
            j2_template = Template(blog_page_template)
            html = j2_template.render(template_parameters)

            # Write out the page to file
            with open(self.make_page_name(page_index), mode='w') as f:
                f.write(html)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    generator = BlogPagesGenerator()
    generator.generate_pages()

