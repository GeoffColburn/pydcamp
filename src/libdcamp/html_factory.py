#!/usr/bin/env python
import sys, os
import sqlite3

import extern.markup as markup
from extern.markup import oneliner as e
from breseq.genome_diff import GenomeDiff


class HtmlFactory:

    def __init__(self, settings):
        self.settings = settings
        assert os.path.exists(self.settings.results_dcamp_paths_db_pth)
        self.con = sqlite3.connect(self.settings.results_dcamp_paths_db_pth)
        self.cur = self.con.cursor() 

    def TablesInDb(self):
        ret_val = list()
        for table in self.cur.execute("select name from sqlite_master where type='table'"):
            ret_val.append(table[0])
        return ret_val


    def WriteHeader(self, page):
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

    def WriteValidationContent(self, page, key = "", title = ""):
        page.div(class_ = "content_container")

        page.div(class_ = "content_left_nav")
        page.ul()
        for pipeline in self.TablesInDb():
            self.cur.execute("select run_name from {}".format(pipeline))
            for run_name, in self.cur.fetchall(): pass

        
        page.ul.close()



        page.div.close()#End content_left_nav.
        
        #for pipeline in self.TablesInDb():
        #    self.cur.exectue("select run_name, {} from {}".format(key, pipeline)

        page.div.close()#End content_container.

        return page


    def CreateIndexPage(self, path):
        page = markup.page()
        css = ["dcamp_style.css", "pro_dropdown_3/pro_dropdown_3.css"]
        script = {"pro_dropdown_3/stuHover.js":"javascript"}
        page.init(css = css, script = script)

        page.div(class_ = "main_container")
        page = self.WriteHeader(page)
        page.div.close()

        open(path, 'w').write(str(page) + '\n')


    def CreateValidationPage(self, path, key = "", title = ""):
        page = markup.page()
        css = ["dcamp_style.css", "pro_dropdown_3/pro_dropdown_3.css"]
        script = {"pro_dropdown_3/stuHover.js":"javascript"}
        page.init(css = css, script = script)

        page.div(class_ = "main_container")
        page = self.WriteHeader(page)

        page = self.WriteValidationContent(page)


        page.div.close() #Main container


        open(path, 'w').write(str(page) + '\n')
