from jinja2 import Template


MAX_HEADER_LENGTH = 5

RETURN = "\n"
RESERVED_LINES_MAX_INDEX = 1


class PostConvertor:
    def __init__(self, input_filename):
        self._input_filename = input_filename

    def make_post_html(self, meta_description, background_image_name, post_date):

        # Load post template
        html_template = ""
        with open("post_template.html", mode='r') as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                html_template += line

        # Convert article to html

        # Load the article
        article_lines = list()
        with open(self._input_filename, mode="r", encoding='utf-8-sig') as f:
            article_lines = f.readlines()
        if len(article_lines) == 0:
            print("Failed to load article!!!")
            return None

        # Detect the title
        title = article_lines[0].replace(RETURN, "")

        # Subtitle is always the second line, if its not empty
        sub_title = ""
        if article_lines[1] is not None or article_lines[1] is not RETURN:
            sub_title = article_lines[1].replace(RETURN, "")

        # Parse the rest for the article text
        article_text = ""
        paragraph = ""
        first_line_index = 0
        first_line_found = False
        recording_paragraph = False
        for i, line in enumerate(article_lines):

            if i <= RESERVED_LINES_MAX_INDEX:
                continue

            skip_tabs = False
            if i <= first_line_index:
                skip_tabs = True

            # Remove the return from the line
            line = line.replace(RETURN, "")

            # Handle headings
            if self.is_heading(line):
                # Make heading
                heading = self.make_heading(line, skip_tabs)

                # Add to paragraph
                article_text += heading + "\n"
            else:
                # handle body text
                if self.is_break(line):
                    if not first_line_found:
                        first_line_index = i

                    # Only write out when recording
                    if recording_paragraph:
                        # reach an end, make a paragraph and save it to article text
                        paragraph_html = self.make_paragraph(paragraph, skip_tabs)
                        article_text += paragraph_html + "\n"

                    # Reset the paragraph for next time
                    paragraph = ""
                    recording_paragraph = False
                else:

                    # mark we found a non-break line
                    first_line_found = True

                    # start recording
                    recording_paragraph = True

                    # Save off the body
                    paragraph += line

                    # TODO Handle quotes for block quotes
                    # TODO Handle links

        # Write out if recording at the end of the lines
        if recording_paragraph:
            # reach an end, make a paragraph and save it to article text
            paragraph_html = self.make_paragraph(paragraph)
            article_text += paragraph_html + "\n"

        # Fill out template parameters using jinja
        template_parameters = {
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

        return html, template_parameters

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
    from json import encoder

    parser = argparse.ArgumentParser()
    parser.add_argument("--file-in", default=None)
    parser.add_argument("--file-out", default="post.html")
    args = parser.parse_args()

    if args.file_in:

        if "html" in args.file_out.lower():
            generator = PostConvertor(args.file_in)
            html_text, json_data = generator.make_post_html("meta", "background.jpg", "April 1 2020")

            # Write the file out
            with open(args.file_out, mode='w') as f:
                f.write(html_text)
            # Write the json file out
            with open(args.file_out + ".json", mode='w') as f:
                f.write(encoder.JSONEncoder().encode(json_data))
        else:
            print("The output file type is not .html!")
    else:
        print("--file-in not supplied.")
