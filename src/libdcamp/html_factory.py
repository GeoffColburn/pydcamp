#!/usr/bin/env python
import sys, os
import sqlite3
import shutil

import extern.markup as markup
from extern.markup import oneliner as e

from breseq.genome_diff import *
from libdcamp.settings import Settings
from libdcamp.file_wrangler import FileWrangler

class HtmlFactory:

    def __init__(self):
        self.settings = Settings.instance()

    def copy_css_style(self, html_path):
        if not os.path.exists(os.path.dirname(self.settings.job_css_path)):
            os.makedirs(os.path.dirname(self.settings.job_css_path))

        shutil.copy2(self.settings.shared_css_style_path, self.settings.job_css_path)
        return os.path.relpath(self.settings.job_css_path, os.path.dirname(html_path))

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
                    gd = GenomeDiff(path, header_only = True)
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
        print "***Writing {}".format(self.settings.job_index_path)
        page = markup.page()
        css_path = self.copy_css_style(self.settings.job_index_path)
        css = [css_path]
        page.init(css = css_path)
        page = self.create_validation_content(page, job_paths, key = "comp.gd")

        open(self.settings.job_index_path, 'w').write(str(page) + '\n')


def mutation_rate_table(output, union_table):
    print "***Writing {}".format(output)
    
    page = markup.page()
    css = """
    #wrapper {
        margin:0px auto;
        width:800px;
    }

    body {
        text-size:16px;

    }

    table {
        border:3px solid #0B5FA5;
        border-collapse:collapse;
        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
        width:800px;
    }

    th {
        background-color:#25547B;
        padding:2px 7px 2px 7px;
        color:#ffffff;
    }
    
    td {
          border:1px solid black;
          padding:2px 7px 2px 7px;
          text-align:center;
    }

    #third_column_border {
        border-right:3px solid #0B5FA5;
    }

    #alternate_row_color {
        background-color:#BCDEFF;
        color:#000000;
    }
    

    """
    page.init(css_string = css)

    page.div(id = "wrapper")

    for test_name in union_table.keys():
        page.table()

        mut_types = [type for type in DiffEntry.line_specs if len(type) == 3]
        #Header
        #First Row
        page.tr()
        page.th(test_name.replace('_', '').capitalize(), style = "font-size:1.3em", rowspan = 2)
        for mut_type in mut_types:
            page.th(mut_type, colspan = 3)
        page.th()
        page.tr.close()
        #Second Row
        page.tr()
        for mut_type in mut_types:
            page.th("TP", style = "font-size:.8em")
            page.th("FN", style = "font-size:.8em")
            page.th("FP", style = "font-size:.8em")
        page.th("Files")
        page.tr.close()

        #Data Rows
        is_alt = False
        for pipeline, path in union_table[test_name].iteritems():
            gd = GenomeDiff(path)
            
            if is_alt:
                page.tr(id = "alternate_row_color")
            else:
                page.tr()
            is_alt = False if is_alt else True

            page.th(pipeline.capitalize())

            for mut_type in mut_types:
                n_tp = len([mut for mut in gd[mut_type] if "compare" in mut and mut["compare"] == "TP"])
                n_fn = len([mut for mut in gd[mut_type] if "compare" in mut and mut["compare"] == "FN"])
                n_fp = len([mut for mut in gd[mut_type] if "compare" in mut and mut["compare"] == "FP"])
                total = n_tp + n_fn + n_fp
                if total:
                    page.td(n_tp)
                    page.td(n_fn)
                    page.td(n_fp, id = "third_column_border")
                else:
                    page.td('-')
                    page.td('-')
                    page.td('-', id = "third_column_border")

            href = os.path.relpath(path, os.path.split(output)[0])
            page.td(e.a("union.gd", href = href))

            page.tr.close()
            
        page.table.close()
        page.br()
        page.br()

    page.div.close()

    open(output, 'w').write(str(page) + '\n')


