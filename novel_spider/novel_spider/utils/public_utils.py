from novel_spider.models import Author, Novel


def novel_is_exists(novel_name, author_name):
    author = Author.select().where(Author.name == author_name)
    if not author:
        return False

    if Novel.select().where((Novel.novel_name == novel_name) & (Novel.author == author)).exists():
        return True
    else:
        return False
