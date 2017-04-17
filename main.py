#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



#The main difference between the two is that the post submission form and post listings will be on separate pages.

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_submit(self, title="", content="", error="", blogs=""):
        blogs = db.GqlQuery("SELECT * FROM BlogPost "
                           "ORDER BY created DESC "
                           "LIMIT 5 ")

        self.render("main.html", title=title, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_submit()


class SubmitPage(Handler):

    def get(self):
        self.render('submit.html')

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            b = BlogPost(title = title, content = content)
            b.put()

            self.redirect("/blog")
        else:
            error = "Need Title and Content"
            self.render("submit.html", title=title, content=content, error=error)


class DisplayPage(Handler):

    def get(self, id):
        idd = int(id)
        blog = BlogPost.get_by_id(idd)
        title = blog.title
        content = blog.content
        self.render("display.html", title=title, content=content)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/submit', SubmitPage),
    webapp2.Route('/blog/<id:\d+>', DisplayPage)
], debug=True)
