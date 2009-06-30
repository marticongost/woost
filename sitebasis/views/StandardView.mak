#-*- coding: utf-8 -*-
<%inherit file="BaseView.mak"/>

<%!
from cocktail.translations import translations
from cocktail.html import templates
from sitebasis.models import Site, Document

container_classes = "BaseView StandardView"
%>

<%def name="container()">

    <div class="header">
        ${self.header()}
    </div>

    ${self.menu()}

    <div class="main">
        ${self.main()}
    </div>

    <div class="footer">
        ${self.footer()}
    </div>

</%def>

<%def name="header()">    
    ${self.site_title()}
    ${self.identity()}
    ${self.language_selector()}
</%def>

<%def name="site_title()">
    <h1><a href="/">${Site.main.home.title}</a></h1>
</%def>

<%def name="language_selector()">
    ${self.create_language_selector().render()}
</%def>

<%def name="create_language_selector()">
    <%
    selector = templates.new("sitebasis.views.LanguageSelector")
    selector.add_class("language_selector")
    return selector
    %>
</%def>

<%def name="identity()">
    % if user and not user.anonymous:
        <div class="identity">        
            <strong>${translations(user)}</strong>
            <form method="post">
                <button class="logout_button" name="logout" type="submit">
                    ${translations("Logout")}
                </button>
            </form>
        </div>
    % endif
</%def>

<%def name="create_menu()">
    <%
    menu = templates.new("sitebasis.views.Menu")
    menu.add_class("menu")
    menu.root_visible = False
    menu.collapsible = True
    return menu
    %>
</%def>

<%def name="menu()">
    ${self.create_menu().render()}
</%def>

<%def name="main()">
   
    <h2>${document.inner_title or document.title}</h2>

    % if cms.allows(target_instance = document, action = "modify"):
        <div class="toolbar">
            <% backoffice = Document.get_instance(qname = "sitebasis.backoffice") %>
            <a class="edit_link"
               href="${cms.canonical_uri(backoffice, 'content', document.id, 'fields')}">
                ${translations("Action edit")}
            </a>            
        </div>
    % endif

    <div class="content">
        ${self.content()}
    </div>

    ${self.attachments()}
</%def>

<%def name="attachments()">
    % if document.attachments:
        <ul class="attachments">
            % for resource in document.attachments:
                <li>
                    <a href="${resource.uri}" title="${resource.description}">
                        <img
                            src="${cms.icon_uri(resource, icon_size = 16)}"
                            alt="${translations('sitebasis.views.StandardView attachment icon description')}"/>
                        <span>${translations(resource)}</span>
                    </a>
                </li>
            % endfor
        </ul>
    % endif
</%def>

<%def name="footer()">
</%def>

