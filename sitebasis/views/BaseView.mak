# -*- coding: utf-8 -*-
<%!
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.html import StyleSheet
from sitebasis.models import Site

container_classes = "BaseView"
site = Site.main
content_language = get_content_language()
%>

<html lang="${content_language}">
    
    <head>        
        ${self.meta()}      
        ${self.resources()}
    </head>

    <body>
        <div class="${self.attr.container_classes}">
            ${self.container()}
        </div>
    </body>

</html>

<%def name="meta()">
    
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <meta name="Content-Language" content="${content_language}">
    <title>${document.title}</title>

    % if document.description:
        <meta name="description" content="${document.description}">
    % endif
    
    <%            
    keywords = ((site.keywords or "") + " " + (document.keywords or "")).strip()
    %>
    % if keywords:
        <meta name="keywords" content="${keywords}">
    % endif
    
    <link rel="start" title="${site.home.title}" href="/">
    
    ## Alternate languages
    % for language in document.translations:
        % if language != content_language and document.get("enabled", language):
            <link rel="alternate"
                  title="${translations('sitebasis.views.BaseView alternate language link', lang = language)}"
                  href="${cms.language.translate_uri(language = language)}"
                  lang="${language}",
                  hreflang="${language}">
        % endif
    % endfor

    ## Shortcut icon
    <%
    icon = site.icon
    %>
    % if icon:                
        <link rel="Shortcut Icon" type="${icon.mime_type}" href="${icon.uri}">
    % endif
</%def>

<%def name="resource_markup(uri)">
    % if uri.endswith(".css"):
        <link rel="Stylesheet" type="text/css" href="${uri}">
    % elif uri.endswith(".js"):
        <script type="text/javascript" src="${uri}"></script>
    % endif
</%def>

<%def name="resources()">
    ## Inherited resources
    <%
    ancestry = reversed(list(document.ascend_documents(include_self = True)))        
    %>
    % for ancestor in ancestry:
        % for resource in ancestor.branch_resources:
            ${resource_markup(resource.uri)}
        % endfor
    % endfor
            
    ## Page resources
    % for resource in document.page_resources:
        ${resource_markup(resource.uri)}
    % endfor
    
    ## User defined styles for user content
    <link rel="Stylesheet" type="text/css" href="/user_styles/">
</%def>

<%def name="container()">
    ${self.content()}
</%def>

<%def name="content()">
    ${document.body}
</%def>

