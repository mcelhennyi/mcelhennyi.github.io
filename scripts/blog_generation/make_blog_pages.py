from jinja2 import Template
from os import walk


class BlogPost:
    def __init__(self, post_page_href, title, subtitle, post_date):
        self._post_page_href = post_page_href
        self._title = title
        self._subtitle = subtitle
        self._post_date = post_date

    def generate(self):
        # Load post preview template
        blog_preview_template = ""
        with open("post_preview_template.html", mode='r') as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                blog_preview_template += line

        # Fill out parameters for jinja
        post_preview_template_parameters = {
            "post_page_ref": self._post_page_href,
            "title": self._title,
            "subtitle": self._subtitle,
            "post_date": self._post_date,
        }

        # Run jinja
        j2_template = Template(blog_preview_template)
        html = j2_template.render(post_preview_template_parameters)

        return html


class BlogPagesGenerator:
    def __init__(self):
        pass

    def generate_pages(self):

        # Load blog page template
        blog_page_template = ""
        with open("blog_page_template.html", mode='r') as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                blog_page_template += line

        # Query for the blogs
        directories = dict()
        for (dirpath, dirnames, filenames_) in walk("../../blogs/"):
            # Save off all the file names under their directory
            directories["/" + dirpath.split("/")[-1]] = filenames_

        # Process each directory - create a post struct for each
        preview_blocks = []
        for directory in directories.keys():

            # Parse each file in this directory
            for file in directories[directory]:
                # Load the files
                

                # Parse for required data

                #


        print("help")

        # Fill out template parameters using jinja
        blog_page_template_parameters = {
            "meta_description": meta_description,
            "head_title": title + " post",
            "background_image_name": background_image_name,
            "title": title.capitalize(),
            "sub_title": sub_title,
            "post_date": post_date,
            "article_text": article_text,
        }

        # Run jinja
        j2_template = Template(html_template)
        html = j2_template.render(template_parameters)

        return html

    def is_heading(self, line):
        # assert isinstance(line, str)
        line_array = line.split()
        if len(line_array) < MAX_HEADER_LENGTH and len(line_array) > 0:
            return True
        return False

    def is_break(self, line):
        # assert isinstance(line, str)
        if line.isspace() or line is None or line == "":
            return True
        return False

    def make_heading(self, heading, skip_tabs=False):

        heading_html = ""
        if not skip_tabs:
            heading_html = "\t" * 5

        return heading_html + "<h2 class=\"section-heading\">{}</h2>".format(heading)

    def make_paragraph(self, text, skip_tabs=False):
        assert isinstance(text, str)

        paragraph = ""
        if not skip_tabs:
            paragraph = "\t" * 5

        return paragraph + "<p>{}</p>".format(text.replace(RETURN, ""))

    def make_link(self, link_text, link_url):
        return "<a href=\"{}\">{}</a>".format(link_url, link_text)

    def make_block_quote(self, quote_text):
        return "<blockquote>{}</blockquote>".format(quote_text)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    generator = BlogPagesGenerator()
    html_text = generator.generate_pages()

    # Write the file out
    with open(args.file_out, mode='w') as f:
        f.write(html_text)

