# -*- coding: utf-8 -*-

class CommitInfo:
    def __init__(self, author, revision, branch, comment, issue):
        self.author = author
        self.revision = revision
        self.branch = branch
        self.comment = comment
        self.issue = issue

    def __str__(self):
        return '(' + self.branch + ') ' + self.revision + ' ' + self.author + ' : ' + self.comment

    def __repr__(self):
        return '(' + self.branch + ') ' + self.revision + ' ' + self.author + ' : ' + self.comment


class PushInfo:
    def __init__(self, branch, old_revision, new_revision):
        self.branch = branch
        self.old_revision = old_revision
        self.new_revision = new_revision

    def __str__(self):
        return '(' + self.branch + ') ' + self.old_revision + ' -> ' + self.new_revision

    def __repr__(self):
        return '(' + self.branch + ') ' + self.old_revision + ' -> ' + self.new_revision
