# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

def generate_fulladdr_from_path(path):
    """
    Method to generate comma separated full address path given a hierarchy path.

    :param path: '+' separated hierarchy path
    :return: Comma separated address
    """
    s = path.split('+')
    s.reverse()
    return ', '.join(s)