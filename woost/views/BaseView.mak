# -*- coding: utf-8 -*-
<%!
from cocktail.translations import translations
from woost.models import Site, Publishable

output_format = "html4"
container_classes = "BaseView"
site = Site.main
%>

<%def name="closure()" filter="trim">
    ${"/" if self.attr.output_format == "xhtml" else ""}
</%def>

${self.dtd()}

% if self.attr.output_format == "xhtml":
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="${get_language()}" lang="${get_language()}">
% else:
<html lang="${get_language()}">
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
    ${publishable.title}
</%def>

<%def name="get_keywords()">
    <%
        keywords = []
        site_keywords = site.keywords
        if site_keywords:
            keywords.append(site_keywords)
        item_keywords = getattr(publishable, "keywords", None)
        if item_keywords:
            keywords.append(item_keywords)
        return " ".join(keywords) if keywords else None
    %>
</%def>

<%def name="dtd()">
    % if self.attr.output_format == "xhtml":
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    % else:
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> 
    % endif
</%def>

<%def name="meta()">
    
    <meta http-equiv="Content-Type" content="${publishable.mime_type};charset=${publishable.encoding}"${closure()}>
    <meta name="Content-Language" content="${get_language()}"${closure()}>
    <title>${self.getTitle()}</title>

    <%
        description = getattr(publishable, "description", None) or site.description
    %>
    % if description:
        <meta name="description" content="${description}"${closure()}>
    % endif
    
    <%            
    keywords = self.get_keywords()
    %>
    % if keywords:
        <meta name="keywords" content="${keywords}"${closure()}>
    % endif
    
    <link rel="start" title="${site.home.title}" href="/"${closure()}>
    
    ## Alternate languages
    % if publishable.per_language_publication:
        % for language in publishable.translations:
            % if language != get_language() and publishable.get("translation_enabled", language):
                <link rel="alternate"
                      title="${translations('woost.views.BaseView alternate language link', lang = language)}"
                      href="${cms.translate_uri(language = language)}"
                      lang="${language}"
                      hreflang="${language}"${closure()}>
            % endif
        % endfor
    % endif

    ## Shortcut icon
    <%
    icon = site.icon
    %>
    % if icon:                
        <link rel="Shortcut Icon" type="${icon.mime_type}" href="${cms.uri(icon)}"${closure()}>
    % endif
</%def>

<%def name="resource_markup(uri, mime_type = None)">
    % if mime_type == "text/css" or uri.endswith(".css"):
        <link rel="Stylesheet" type="${mime_type or 'text/css'}" href="${uri}"${closure()}>
    % elif mime_type in ("text/javascript", "application/javascript", "text/ecmascript", "application/jscript") or uri.endswith(".js"):
        <script type="${mime_type or 'text/javascript'}" src="${uri}"></script>
    % endif
</%def>

<%def name="resources()">

    ## Resources
    % for resource in publishable.resources:
        ${resource_markup(resource.uri)}
    % endfor
    
    ## User defined styles for user content
    <%
    user_styles = Publishable.get_instance(qname = "woost.user_styles")
    %>
    % if user_styles:
        <link rel="Stylesheet" type="${user_styles.mime_type}" href="${cms.uri(user_styles)}"${closure()}>
    % endif
</%def>

<%def name="container()">
    ${self.content()}
</%def>

<%def name="content()">
    ${publishable.body}
</%def>

