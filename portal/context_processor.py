# -*- coding: utf-8 -*-

def uicontext(request):
    # print("uicontext is called with path info %s" % request.path_info)
    if request.method == 'GET' and request.path_info == '/in-progress-module':
        return {'two_drawers': True}
    else:
        return  {}
