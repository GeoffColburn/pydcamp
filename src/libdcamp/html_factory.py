#!/usr/bin/env python
import sys, os
import sqlite3
import shutil

import extern.markup as markup
from extern.markup import oneliner as e

from breseq.genome_diff import GenomeDiff
from libdcamp.settings import Settings
from libdcamp.job import FileWrangler


class HtmlFactory:

    def __init__(self):
        self.settings = Settings.instance()

    def copy_css_style(self):
        if not os.path.exists(os.path.dirname(self.settings.job_css_path)):
            os.makedirs(os.path.dirname(self.settings.job_css_path))

        shutil.copy2(self.settings.shared_css_style_pth, self.settings.job_css_path)
        return os.path.relpath(self.settings.job_css_path, self.settings.job_dir)

    def write_header(self, page):
        page.div(class_ = "header_container")

        page.div(class_ = "nav_bar")

        #Pro stuffs
        page.span(class_ = "preload1")
        page.span(class_ = "preload2")

        page.ul(id="nav")
        page.li(e.a(e.span("Home"), class_ = "top_link", href = "index.html"), class_ = "top")

        #Validation.
        page.li(class_ = "top")
        page.a(e.span("Validation", class_ = "down"), id = "validation", class_ = "top_link", href = "#")
        page.ul(class_ = "sub")
        page.li(e.b("Original"))
        page.li(e.a("Output", href = "#"))
        page.li(e.a("Only AF < 1.00", href = "#"))
        page.li(e.a("Only AF = 1.00", href = "#"))
        page.li(e.b("Normalized"))
        page.li(e.a("Output", href = "#"))
        page.li(e.a("Only AF < 1.00", href = "#"))
        page.li(e.a("Only AF = 1.00", href = "#"))
        page.ul.close()
        page.li.close()

        #Prediction Rates.
        page.li(class_ = "top")
        page.a(e.span("Predictions", class_ = "down"), id = "predictions", class_ = "top_link", href = "#")
        page.ul(class_ = "sub")
        page.li(e.b("Original"))
        page.li(e.a("Output", href = "#"))
        page.li(e.a("Only AF < 1.00", href = "#"))
        page.li(e.a("Only AF = 1.00", href = "#"))
        page.li(e.b("Normalized"))
        page.li(e.a("Output", href = "#"))
        page.li(e.a("Only AF < 1.00", href = "#"))
        page.li(e.a("Only AF = 1.00", href = "#"))
        page.ul.close()
        page.li.close()

        #Issues.
        page.li(class_ = "top")
        page.a(e.span("Issues", class_ = "down"), id = "issues", class_ = "top_link", href = "#")
        page.ul(class_ = "sub")
        page.li(e.b("Pipeline"))
        page.li(e.a("", href = "#"))
        page.ul.close()
        page.li.close()


        page.ul.close()
        page.div.close()#End nav_bar 


        page.div.close()#End header

        return page

    def create_validation_content(self, page, job_paths, key = "", title = ""):
        wrangler = FileWrangler(job_paths, key)
        page.div(id = "validation_table")
        #Table header.
        page.table()
        page.tr()
        page.th()#Empty one to offset run_names below it.
        for job_id in wrangler.job_ids:
            page.th(job_id.capitalize(), class_ = "validation_table", colspan = 3)
        page.th()
        page.tr.close()
        page.tr()
        page.th("Name")
        for i in wrangler.job_ids:
            page.th("TP")
            page.th("FN")
            page.th("FP")
        page.th("Files")
        page.tr.close()

        #Table data.
        is_alt = False

        for run_id in wrangler.run_ids:
            if is_alt:
                page.tr(class_ = "alternate_row")
            else:
                page.tr()
            is_alt = False if is_alt else True

            page.th(run_id)
            file_anchors = list()
            for job_id in wrangler.job_ids:
                if wrangler.file_exists(job_id, run_id):
                    path = wrangler.get_file(job_id, run_id)
                    gd = GenomeDiff(path)
                    header_info = gd.header_info()
                    assert "TP|FN|FP" in header_info.other
                    validation = header_info.other["TP|FN|FP"].split('|')
                    tp = validation[0]
                    fn = validation[1]
                    fp = validation[2]
                    page.td(tp, class_ = "validation_table_column")
                    page.td(fn, class_ = "validation_table_column")
                    page.td(fp, class_ = "validation_table_last_column")
                    href = os.path.relpath(path, self.settings.job_dir)
                    file_anchors.append(e.a(job_id.capitalize(), href = href))
                else:
                    page.td('-', class_ = "validation_table_column")
                    page.td('-', class_ = "validation_table_column")
                    page.td('-', class_ = "validation_table_last_column")


            page.th("/".join(file_anchors))

            page.tr.close()
        page.table.close()
        page.div.close()
        return page

    def write_index_page(self, job_paths):
        page = markup.page()
        css_path = self.copy_css_style()
        css = [css_path]
        page.init(css = css_path)
        page = self.create_validation_content(page, job_paths, key = "comp.gd")

        open(self.settings.job_index_path, 'w').write(str(page) + '\n')


    def create_validation_page(self, path, key = "", title = ""):
        page = markup.page()
        css = ["dcamp_style.css", "pro_dropdown_3/pro_dropdown_3.css"]
        script = {"pro_dropdown_3/stuHover.js":"javascript"}
        page.init(css = css, script = script)

        page.div(class_ = "main_container")
        page = self.write_header(page)

        page = self.write_validationcontent(page)


        page.div.close() #Main container


        open(path, 'w').write(str(page) + '\n')
