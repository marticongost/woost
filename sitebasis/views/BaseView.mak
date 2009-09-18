# -*- coding: utf-8 -*-
<%!
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.html import StyleSheet
from sitebasis.models import Site

output_format = "html4"
container_classes = "BaseView"
site = Site.main
content_language = get_content_language()
%>

<%def name="closure()" filter="trim">
    ${"/" if self.attr.output_format == "xhtml" else ""}
</%def>

${self.dtd()}

% if self.attr.output_format == "xhtml":
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="${content_language}" lang="${content_language}">
% else:
<html lang="${content_language}">
% endif
    
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

<%def name="getTitle()">
    ${document.title}
</%def>

<%def name="dtd()">
    % if self.attr.output_format == "xhtml":
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    % else:
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> 
    % endif
</%def>

<%def name="meta()">
    
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8"${closure()}>
    <meta name="Content-Language" content="${content_language}"${closure()}>
    <title>${self.getTitle()}</title>

    <% 
    description = document.description or site.description
    %>
    % if description:
        <meta name="description" content="${description}"${closure()}>
    % endif
    
    <%            
    keywords = ((site.keywords or "") + " " + (document.keywords or "")).strip()
    %>
    % if keywords:
        <meta name="keywords" content="${keywords}"${closure()}>
    % endif
    
    <link rel="start" title="${site.home.title}" href="/"${closure()}>
    
    ## Alternate languages
    % for language in document.translations:
        % if language != content_language and document.get("enabled", language):
            <link rel="alternate"
                  title="${translations('sitebasis.views.BaseView alternate language link', lang = language)}"
                  href="${cms.language.translate_uri(language = language)}"
                  lang="${language}",
                  hreflang="${language}"${closure()}>
        % endif
    % endfor

    ## Shortcut icon
    <%
    icon = site.icon
    %>
    % if icon:                
        <link rel="Shortcut Icon" type="${icon.mime_type}" href="${icon.uri}"${closure()}>
    % endif
</%def>

<%def name="resource_markup(uri)">
    % if uri.endswith(".css"):
        <link rel="Stylesheet" type="text/css" href="${uri}"${closure()}>
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
    <link rel="Stylesheet" type="text/css" href="/user_styles/"${closure()}>
</%def>

<%def name="container()">
    ${self.content()}
</%def>

<%def name="content()">
    ${document.body}
</%def>

